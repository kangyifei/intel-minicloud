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

# redis内存数据库用作进程通信
sessionPool=redis.Redis(host='localhost',port=6379)#内存会话记录
# ===========================================
#测试
class RESTExample(Resource):
    def get(self):
        return {'msg': 'ok example'}

    def post(self):
        abort(400) # 取消


# 上传节点信息
class RESTNodeInfo(Resource):
    def get(self):
        pass
    
    # 通过post上传节点信息，python中使用 request.post即可上传
    def post(self):
        id = request.form['id']
        cpu = request.form['cpu']
        memory = request.form['memory']
        hdd = request.form['hdd']

        print(cpu, memory, hdd)

        return {'msg': 'success'}