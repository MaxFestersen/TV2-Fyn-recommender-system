from surprise import Reader, SVDpp
from surprise.dataset import Dataset
from surprise.model_selection import GridSearchCV
from surprise import dump
from recommenders.utils.timer import Timer
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))
from utility.data_optimized import allUsers

data = allUsers().interactions()[['deviceID', 'articleID', 'affinity']]
reader = Reader() # rating scale should be specified
data = Dataset.load_from_df(data, reader)

param_grid = {'n_factors': [5, 10, 15, 20, 25, 30, 35], 
            'n_epochs': [5, 10, 15, 20, 25, 30, 35], 
            'lr_all': [0.002, 0.005, 0.007, 0.01],
            'reg_all': [0.2, 0.4, 0.6, 0.8]}

gs = GridSearchCV(SVDpp, param_grid, measures=['rmse', 'mae'], cv=3)
with Timer() as grid_time:
    gs.fit(data)
    
print(f'Grid Search took {grid_time.interval} seconds')
print('Best RMSE score is {} with parameters:'.format(gs.best_score['rmse']))
print(gs.best_params['rmse'])

model = gs.best_estimator['rmse']
trainset = data.build_full_trainset()
model.fit(trainset)

dump.dump('./SVDpp_model', model) # saving fitted model
