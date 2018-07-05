from flask_restful import Resource,reqparse,abort
from flask import request,Flask,url_for,send_from_directory
from werkzeug.security import safe_join as safe_join
from datetime import date,timedelta,datetime
import flask_restful as restful
import requests
import re
import json
import redis
import hashlib
import os

parser=reqparse.RequestParser()
parser.add_argument('type',type=str)
# ===========================================
#测试
class RESTExample(Resource):
    def get(self):
        return {'msg': 'ok example'}

    def post(self):
        abort(400) # ??????????