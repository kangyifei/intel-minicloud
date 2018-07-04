from flask import Flask
from flask_cors import CORS
from flask_restful import Resource,abort,reqparse
import flask_restful as restful
import os
from REST import RESTExample
import datetime

app = Flask(__name__)

CORS(app) #跨域
api = restful.Api(app)

# ==================================================
# 接口列表，将/example路由到RESTExample类
api.add_resource(RESTExample, '/example')
# ===================================================

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
