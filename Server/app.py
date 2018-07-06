import sys
from flask import Flask
from flask_cors import CORS
from flask_restful import Resource,abort,reqparse
import flask_restful as restful
import datetime
import docker
from flask import request,Flask,url_for,send_from_directory
from werkzeug.security import safe_join as safe_join
from datetime import date,timedelta,datetime
import requests
import re
import json
import redis
import hashlib
import os


# 存储当前cpu负载的全局变量，键值对的形式存储，{id: cpuload}，使用cpuLoadCurrent['$id'] 即可访问$id的CPU负载
cpuLoadCurrent = {}



app = Flask(__name__)
CORS(app) #跨域


# get参数解析器
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

        cpuLoadCurrent[id] = cpu

        return {'msg': 'success'}

# ==================================================
api = restful.Api(app)
# 接口列表，将/example路由到RESTExample类
api.add_resource(RESTExample, '/example')

# 节点负载信息接口
api.add_resource(RESTNodeInfo, '/nodeinfo')
# ===================================================

if __name__ == '__main__':
    # client = docker.from_env()
    # if not client.swarm.init(advertise_addr="192.168.1.145:2377"):
    #     sys.exit("swarm init failed")
    # swarm_attr=client.swarm.attrs
    # worker_token=swarm_attr['JoinTokens']['Worker']

    app.run(host="0.0.0.0", port=5000, debug=True)

