#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# API libraries
from flask import Flask
from flask_restful import Resource, Api
from apispec import APISpec
from marshmallow import Schema, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc

from data import UserHistory


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

# Defining the response schema of articles
class article_schema(Schema):
    articleID = fields.List(fields.String(), description='list of bazo ID\'s of articles read by user')
    deviceID = fields.String(description='User ID set by cookie')

class ContentBased(UserHistory, MethodResource, Resource):
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
        articleIDs = self.articleIDs(deviceID)
        return {'deviceID': deviceID, 'articleID': articleIDs}

class CollaborativeFiltering(UserHistory, MethodResource, Resource):
    @doc(description='Get all articleID\'s of a specific users history', tags=['Collaborative Filtering'])
    @marshal_with(article_schema) # marshalling
    def get(self, deviceID: str):
        '''
        Get method represents a GET API method
        '''
        articleIDs = self.articleIDs(deviceID)
        return {'deviceID': deviceID, 'articleID': articleIDs}

api.add_resource(ContentBased, '/api/ContentBased/<string:deviceID>')
api.add_resource(CollaborativeFiltering, '/api/CollabFiltering/<string:deviceID>')
docs.register(ContentBased)
docs.register(CollaborativeFiltering)

if __name__ == '__main__':
    app.run(debug=True)
    