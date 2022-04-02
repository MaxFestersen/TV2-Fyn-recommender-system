#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# API libraries
from datetime import date
from flask import Flask, request, Response
from flask_restful import Resource, Api, reqparse
from apispec import APISpec
from marshmallow import Schema, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc
from numpy import float16
from waitress import serve
from surprise import dump
from data_optimized import allUsers, User, CookieDatabase
import tensorflow as tf
import os

# API
app = Flask(__name__)  # Flask app instance initiated
api = Api(app)  # Flask restful wraps Flask app around it.
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='TV2Fyn recommender system',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='3.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/',  # URI to access UI of API Doc
})

# Initiating the swagger docs
docs = FlaskApiSpec(app)

parser = reqparse.RequestParser()
parser.add_argument('from', type=str, required=True)
parser.add_argument('to', type=str, default=str(date.today()), required=False)
parser.add_argument('titles', type=bool, default=False, required=False)

# Defining the response schema of articles
class article_schema(Schema):
    articleID = fields.List(fields.String(), description='list of bazo ID\'s of articles read by user')
    deviceID = fields.String(description='User ID set by cookie')

class ContentBased(MethodResource, Resource):
    @doc(description='Get all articleID\'s of a specific users history', tags=['Content Based'])
    @marshal_with(article_schema) # marshalling
    def get(self, deviceID: str):
        '''
            get:
                description: 
                responses:
                    200:
                description: 
                content:
                    application/json:
                        schema: articleSchema
        '''
        pass

class CollaborativeFiltering(MethodResource, Resource):
    
    model, _ = dump.load('./SVDpp_model')
    articleIDs = CookieDatabase().allArticleIDs()

    def getRecommendations(self, deviceID: str):
        ratings = [self.model.predict(uid=deviceID, iid=iid).est for iid in self.articleIDs]
        predictions = dict(zip(self.articleIDs, ratings))
        return sorted(predictions.items(), key=lambda x:x[1], reverse=True)
        
    @doc(description='Get all articleID\'s of a specific users history', tags=['Collaborative Filtering'])
    def get(self, deviceID: str):
        '''
            get:
                description: Get method for CollaborativeFiltering
        '''
        u = User(deviceID)
        articleIDs = u.articleIDs()
        recs = self.getRecommendations(deviceID)
        return {k: v for k,v in recs if k not in articleIDs}

class DCN(MethodResource, Resource):
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    model = tf.saved_model.load('DCN')

    @doc(description='Get Deep Cross Network recommendations for a specific user', tags=['Deep Cross Network'])
    def get(self, deviceID: str):
        u = User(deviceID)
        data = dict(u.antiInteractions())
        recs = self.model(data)
        return dict(zip(data['articleID'], tf.squeeze(recs).numpy().astype(str)))

class avgScrollAPI(allUsers, MethodResource, Resource):
    @doc(description='Get average scroll of users per articleID or title', tags=['Evaluation'])
    def get(self):
        '''
            get:
                description: Get method for avgScroll
        '''
        args = parser.parse_args()
        _from = args['from']
        _to = args['to']
        titles = args['titles']
        a = allUsers()
        df = a.avgScroll(_from, _to, titles)
        return Response(df.to_json(orient='records'), mimetype='application/json')

class avgElapsedAPI(allUsers, MethodResource, Resource):
    @doc(description='Get average elapsed time of users per articleID or title', tags=['Evaluation'])
    def get(self):
        '''
            get:
                description: Get method for avgScroll
        '''
        args = parser.parse_args()
        _from = args['from']
        _to = args['to']
        titles = args['titles']
        a = allUsers()
        df = a.avgElapsed(_from, _to, titles)
        return Response(df.to_json(orient='records'), mimetype='application/json')

api.add_resource(ContentBased, '/api/ContentBased/<string:deviceID>')
api.add_resource(CollaborativeFiltering, '/api/CollabFiltering/<string:deviceID>')
api.add_resource(DCN, '/api/DCN/<string:deviceID>')
api.add_resource(avgScrollAPI, '/api/avgscroll')
api.add_resource(avgElapsedAPI, '/api/avgelapsed')
docs.register(avgScrollAPI)
docs.register(avgElapsedAPI)
docs.register(ContentBased)
docs.register(CollaborativeFiltering)
docs.register(DCN)

if __name__ == '__main__':
    app.run(debug=True) #development server
    #serve(app, host='0.0.0.0', port=8080) #production server
    