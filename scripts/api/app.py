#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Resource, Api
from apispec import APISpec
from marshmallow import Schema, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

# Database requests
import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
db_host = os.environ.get('db-host')
db_user = os.environ.get('db-user')
db_pass = os.environ.get('db-pass')

mydb = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database='tv2fyn')

mycursor = mydb.cursor()

def get_sessions(deviceID):
    mycursor.execute(f'SELECT sessionID FROM session WHERE deviceID="{deviceID}";')
    session = mycursor.fetchall()
    sessionID = list(map(lambda x: x[0], session))
    return sessionID

def get_sessionInfo(sessionID):
    mycursor.execute(f'SELECT articleID FROM sessionInfo WHERE sessionID="{sessionID}";')
    sessionInfo = mycursor.fetchall()
    return sessionInfo


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
docs = FlaskApiSpec(app)

class user_schema(Schema):
    deviceID = fields.Str()
    articleID = fields.List(fields.Str())


#  Restful way of creating APIs through Flask Restful
class RecommenderAPI(MethodResource, Resource):
    @doc(description='Get articleID of a specific user', tags=['user-id'])
    @marshal_with(user_schema)  # marshalling
    def get(self, deviceID: str):
        '''
        Get method represents a GET API method
        '''
        sessionID = get_sessions(deviceID)
        articleID = list(map(lambda x: get_sessionInfo(x), sessionID))
        return {'deviceID': f'{deviceID}',
        'articleID': articleID}

api.add_resource(RecommenderAPI, '/articles/<string:deviceID>')
docs.register(RecommenderAPI)

if __name__ == '__main__':
    app.run(debug=True)
    