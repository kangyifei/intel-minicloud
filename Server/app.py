from gevent import monkey; monkey.patch_all()
import shutil
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
import gevent


# 存储当前节点预测模型的全局变量，键值对的形式存储，{id: GBRT}，使用['$id'] 即可访问$id的预测模型
from DirectlyDockerBuild import DirectlyDockerBuilder
from GBRT.GBRT import GBRT
nodesGBRT={}

# 算力共享任务
from ComputingShare import ComputingShareTask, ComputingShareTasks
computingTasks = ComputingShareTasks()
#获取本地DOCKER客户端
client = docker.from_env()

app = Flask(__name__)
CORS(app) #跨域

# 任务
threads = []

# get参数解析器
parser=reqparse.RequestParser()
parser.add_argument('type',type=str)

# redis内存数据库用作进程通信
sessionPool=redis.Redis(host='localhost',port=6379)#内存会话记录

FILE_FOLDER = './files'  # 上传文件目录
DOCKER_FOLDER = FILE_FOLDER + '/docker' # docker文件存储目录
PROGRAM_FOLDER = FILE_FOLDER + '/program' # 程序上传目录
DATA_FOLDER = FILE_FOLDER + '/data' # 数据上传目录
RESULT_FOLDER = FILE_FOLDER + '/result' # 结果上传目录

ALLOWED_FOLDERS = [DOCKER_FOLDER, PROGRAM_FOLDER, DATA_FOLDER, RESULT_FOLDER] # 所有允许上传和文件目录集合
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
        time=request.form['time']
        cpu = request.form['cpu']
        memory = request.form['memory']
        hdd = request.form['hdd']
        print(cpu, memory, hdd)
        ##利用新上传的cpu负载训练模型
        if id in nodesGBRT:
            nodesGBRT[id].update(time,cpu)
        else:
            nodesGBRT[id]=GBRT(n_trees=100)
            nodesGBRT[id].update(time, cpu)
        ##结束

        return {'msg': 'success'}, 200

# 上传文件接口, 通过post方式上传
class RESTUpload(Resource):
    def post(self, folder):
        # 从请求体中获得文件
        myfile = request.files['file']

        # 拼接存储目录
        destFolder = FILE_FOLDER + '/' + folder

        # 如果不在允许的目录内，则返回错误码
        if destFolder not in ALLOWED_FOLDERS:
            return {"msg": "fail, folder name error"}, 400

        if myfile: # 文件存在
            filename = myfile.filename # 获取文件名

            fullFileName = destFolder + '/' + filename

            myfile.save(destFolder + '/' + filename) # 保存

            return {"msg": "success", 'filename': filename}, 200
        else:
            return {"msg": "fail, file not exists"}, 400
    
    def get(self, folder):
        return {'msg': folder}

# 算力共享平台分发接口，接收参数为程序名和数据包名，其中，程序为单个可执行文件，数据包后缀为tar.gz
class RESTComputingTasks(Resource):
    def post(self):
        try:
            programName = request.form['programName']
            dataName = request.form['dataName']
            nodeIdsStr = request.form['nodeIds']
            nodeIds = json.loads(nodeIdsStr)
        except:
            return {'msg': 'arguments illegal'}, 400

        programFullName = PROGRAM_FOLDER + '/' + programName
        dataFullName = DATA_FOLDER + '/' + dataName

        computingTasks.newTask(programFullName, dataFullName) # 新建算力共享任务

        return {"msg": "success"}, 200

class RESTFiles(Resource):
    def get(self, folder, filename):
        return send_from_directory(FILE_FOLDER + '/' + folder, filename)

    def delete(self, folder, filename):
        try:
            os.remove(FILE_FOLDER + '/' + folder + '/' + filename)
        except:
            return {"msg": "file not exists"}, 410
        else:
            return {"msg": "delete success"}, 200


# docker分发接口.docker文件名从url中解析得到，分发的目标节点id从post接口中得到
##TODO:增加了DOCKER分发的tag标签，即镜像的名字，可以是name,自动变成name:lastest;或者是name:version
##TODO:增加了DOCKER分发的num属性，即要分发多少个容器
class RESTDockerDeploy(Resource):
    def post(self):

        try: 
            dockerName = request.form['dockerName']
            tag = request.form['tag']
            num = request.form['num']

            nodeIdsStr = request.form['nodeIds']
            nodeIds = json.loads(nodeIdsStr)

            dockerFullPath = DOCKER_FOLDER + '/' + dockerName # 完整docker路径
            newDockerfolder=DOCKER_FOLDER + '/' + dockerName+"_folder"
            os.mkdir(newDockerfolder)

        except:
            return {'msg': 'deploy failed'}, 400


        shutil.copy(dockerFullPath,DOCKER_FOLDER + '/' + dockerName+"_folder"+"/Dockerfile")
        image=DirectlyDockerBuilder(newDockerfolder,tag).build()
        import docker.types
        client.services.create(image=image,
                               name=tag,
                               mode=docker.types.ServiceMode(mode="replicated",replicas=int(num)))
        print(dockerFullPath)

        return {'msg': 'deploy success'}, 200


# ==================================================
api = restful.Api(app)
# 接口列表，将/example路由到RESTExample类
api.add_resource(RESTExample, '/example')
# 节点负载信息接口
api.add_resource(RESTNodeInfo, '/nodeinfo')
# 文件上传接口,比如 /upload/docker则是向docker文件夹上传文件，文件名不能与已有文件重复
api.add_resource(RESTUpload, '/upload/<string:folder>')
# 文件管理接口,下载和删除
api.add_resource(RESTFiles, '/files/<string:folder>/<string:filename>')
# docker分发接口，比如 /deploy/docker001 ，参数中 nodeIds = [5, 3, 56]，则是向 5, 3, 56分发镜像
api.add_resource(RESTDockerDeploy, '/dockerdeploy')
# 算力共享平台
api.add_resource(RESTComputingTasks, '/computingtasks')
# ===================================================
# 初始化工作目录
def initWorkSpace():
    # 如果存储文件的文件夹不存在，则创建
    for folder in ALLOWED_FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print("mkdir " + folder + " success!")

# ===================================================

if __name__ == '__main__':

    # 初始化工作目录
    initWorkSpace()
    
    # 添加协程
    threads.append(gevent.spawn(app.run, host="0.0.0.0", port=5000, debug=True)) # flask web服务

    # 等待所有协程结束
    gevent.joinall(threads)
   

    app.run(host="0.0.0.0", port=5000, debug=True)

