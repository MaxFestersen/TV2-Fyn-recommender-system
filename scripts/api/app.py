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

# Database libraries
from mysql.connector import connect
from dotenv import load_dotenv
import os

# Api
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
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})

# Initiating the swagger docs
docs = FlaskApiSpec(app)

# Defining the response schema of articles
class article_schema(Schema):
    deviceID = fields.Str(required=True)
    articleID = fields.List(fields.Str())

# Defining RecommenderAPI 
class RecommenderAPI(MethodResource, Resource):

    # Connecting to cookie database
    load_dotenv()
    db=connect(
        host=os.environ.get('db-host'),
        user=os.environ.get('db-user'),
        password=os.environ.get('db-pass'),
        database=os.environ.get('db-database'))
    cursor = db.cursor()

    def sessions(self, deviceID: str):
        '''
        Function for getting sessionID's of a given user from cookie database
        '''
        self.cursor.execute(f'SELECT sessionID FROM session WHERE deviceID="{deviceID}";')
        sessions = self.cursor.fetchall()
        return list(sum(sessions, ()))
    
    def articles(self, sessions: list):
        '''
        Function for getting articleID's of a users session from cookie database
        '''
        self.cursor.execute('SELECT articleID FROM sessionInfo WHERE sessionID IN {};'.format('(' + ', '.join(f'"{s}"' for s in sessions) + ')'))
        articles = self.cursor.fetchall()
        return list(sum(articles, ()))

    @doc(description='Get all articleID\'s of a specific users history', tags=['Content Based'])
    @marshal_with(article_schema)  # marshalling
    def get(self, deviceID: str):
        '''
        Get method represents a GET API method
        '''
        sessionID = self.sessions(deviceID)
        articleID = self.articles(sessionID)
        #articleID = list(map(lambda x: self.articles(x), sessionID))
        return {'deviceID': f'{deviceID}', 'articleID': articleID}

api.add_resource(RecommenderAPI, '/articles/<string:deviceID>')
docs.register(RecommenderAPI)

if __name__ == '__main__':
    app.run(debug=True)
    