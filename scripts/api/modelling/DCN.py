import tensorflow as tf
import tensorflow_recommenders as tfrs
from tensorflow.keras import Sequential
from tensorflow.keras.layers import StringLookup, IntegerLookup, Embedding, Dense, Discretization, Normalization, TextVectorization, GlobalAveragePooling1D, GRU

class DCN(tfrs.Model):

    def __init__(self, feature_dict: dict, use_cross_layer: bool, n_cross_layers: int, deep_layer_size: list, vocabularies: dict, projection_dim=None):
        super().__init__()
        self.n_cross_layers = n_cross_layers

        self.embedding_dimension = 32
        self.max_tokens = 10_000

        self.str_features = feature_dict.get('str_features')
        self.int_features = feature_dict.get('int_features')
        self.text_features = feature_dict.get('text_features')
        self.cont_features = feature_dict.get('cont_features')
        self.disc_features = feature_dict.get('disc_features')
        self.seq_features = feature_dict.get('seq_features')
        
        self._all_features = self.str_features + self.int_features + self.text_features + self.disc_features + self.seq_features
        self._embeddings = {}
        self._embeddings_cont = {}

        # Create embeddings for str features
        for feature in self.str_features:
            vocabulary = vocabularies[feature]
            self._embeddings[feature] = Sequential([
                StringLookup(
                    vocabulary=vocabulary, mask_token=None),
                Embedding(len(vocabulary) + 1, self.embedding_dimension)
            ], name=feature)
        
        # Create embeddings for int features
        for feature in self.int_features:
            vocabulary = vocabularies[feature]
            self._embeddings[feature] = Sequential([
                IntegerLookup(
                    vocabulary=vocabulary, mask_token=None),
                Embedding(len(vocabulary) + 1, self.embedding_dimension)
            ], name=feature)

        # Create embeddings for text features
        for feature in self.text_features:
            vectorizer = TextVectorization(
                max_tokens=self.max_tokens,
                standardize='lower_and_strip_punctuation',
                ngrams=3
            )
            self._embeddings[feature] = Sequential([
                vectorizer,
                Embedding(self.max_tokens, self.embedding_dimension, mask_zero=True),
                GlobalAveragePooling1D()
            ], name=feature)
            vectorizer.adapt(vocabularies[feature])
        
        # Create embeddings for continuous features
        for feature in self.cont_features:
            vocab = vocabularies[feature][0]
            normalized = Normalization(
                axis=None,
                name=feature
            )
            normalized.adapt(vocab)
            self._embeddings_cont[feature] = normalized
        
        # Create embeddings for discrete features
        for feature in self.disc_features:
            vocab = vocabularies[feature][1]
            self._embeddings[feature] = Sequential([
                Discretization(vocab.tolist()),
                Embedding(len(vocab) + 1, self.embedding_dimension)
            ], name=feature)
        
        for feature in self.seq_features:
            vocab = vocabularies[feature]
            self._embeddings[feature] = Sequential([
                StringLookup(
                    vocabulary=vocab, mask_token=None),
                Embedding(len(vocab) + 1, self.embedding_dimension),
                GRU(self.embedding_dimension),
            ], name=feature)

        
        if use_cross_layer:
            self._cross_layer = tfrs.layers.dcn.Cross(
                projection_dim=projection_dim,
                kernel_initializer='glorot_uniform'
            )
        else:
            self._cross_layer = None
        
        self._deep_layers = [Dense(layer_size, activation='relu') for layer_size in deep_layer_size]
        
        self._logit_layer = Dense(1)

        self.task = tfrs.tasks.Ranking(
            loss = tf.keras.losses.MeanSquaredError(),
            metrics = [tf.keras.metrics.RootMeanSquaredError("RMSE")]
        )

    def call(self, inputs):
        embeddings = []
        for feature in self._all_features:
            embedding_fn = self._embeddings[feature]
            embeddings.append(embedding_fn(inputs[feature]))
        
        for feature in self.cont_features:
            embedding_fn = self._embeddings_cont[feature]
            embeddings.append(tf.reshape(embedding_fn(inputs[feature]), (-1,1)))

        x = tf.concat(embeddings, axis=1)

        # Build Cross Network
        if self._cross_layer is not None:
            layers = []
            for i in range(self.n_cross_layers):
                layers.append(self._cross_layer(x))
            if len(layers) > 0:
                x = tf.concat(layers, axis=1)
        
        # Build Deep Network
        for deep_layer in self._deep_layers:
            x = deep_layer(x)
        
        return self._logit_layer(x)

    def compute_loss(self, inputs, training: bool = False):
        labels = inputs.pop('affinity')
        scores = self(inputs)
        return self.task(
            labels=labels,
            predictions=scores
        )
