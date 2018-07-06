import sys

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource,abort,reqparse
import flask_restful as restful
import os
from REST import RESTExample,RESTNodeInfo
import datetime
import docker
app = Flask(__name__)

CORS(app) #跨域
api = restful.Api(app)

# ==================================================
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

