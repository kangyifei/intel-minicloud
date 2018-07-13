from ServiceBuilder import ServiceBuilder

import shutil
from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, abort, reqparse
import flask_restful as restful
import docker
from flask import request, Flask, url_for, send_from_directory
import json
import redis
import os
from Utils.Utils import formatSize

# 存储当前节点预测模型的全局变量，键值对的形式存储，{id: GBRT}，使用['$id'] 即可访问$id的预测模型
from ImageBuild import ImageBuilder
from GBRT.GBRT import GBRT

nodesGBRT = {}

# 存储所有节点信息的变量
nodeInfo = {}

# 算力共享任务
from ComputingShare import ComputingShareTask

computingShareTask = None

# 获取本地DOCKER客户端
client = docker.from_env()

app = Flask(__name__)
CORS(app)  # 跨域

# 任务
threads = []

# get参数解析器
parser = reqparse.RequestParser()
parser.add_argument('type', type=str)
parser.add_argument('status', type=str)

# redis内存数据库用作进程通信
sessionPool = redis.Redis(host='localhost', port=6379)  # 内存会话记录

FILE_FOLDER = './files'  # 上传文件目录
DOCKER_FOLDER = FILE_FOLDER + '/docker'  # docker文件存储目录
PROGRAM_FOLDER = FILE_FOLDER + '/program'  # 程序上传目录
DATA_FOLDER = FILE_FOLDER + '/data'  # 数据上传目录
RESULT_FOLDER = FILE_FOLDER + '/result'  # 结果上传目录
TEMP_FOLDER = FILE_FOLDER + '/temp'

ALLOWED_FOLDERS = [DOCKER_FOLDER, PROGRAM_FOLDER, DATA_FOLDER, RESULT_FOLDER, TEMP_FOLDER]  # 所有允许上传和文件目录集合


# ===========================================
# 测试
class RESTExample(Resource):
    def get(self):
        return {'msg': 'ok example'}

    def post(self):
        abort(400)  # 取消


# 上传节点信息
class RESTNodeInfo(Resource):
    def get(self):
        data = []
        for k, v in nodeInfo.items():
            n = {
                'id': k,
                'time': v['time'],
                'cpu': v['cpu'],
                'memory': v['memory'],
                'hdd': v['hdd']
            }
            data.append(n)
        return {'msg': 'success', 'data': data}

    # 通过post上传节点信息，python中使用 request.post即可上传
    def post(self):
        id = request.form['id']
        time = int(request.form['time'])
        cpu = int(float(request.form['cpu']))
        memory = request.form['memory']
        hdd = request.form['hdd']

        nodeInfo[id] = {
            'time': time,
            'cpu': cpu,
            'memory': memory,
            'hdd': hdd
        }
        ##利用新上传的cpu负载训练模型
        if id in nodesGBRT:
            # nodesGBRT[id].update([time], [cpu])
            pass
        else:
            nodesGBRT[id] = GBRT(n_trees=100)
            # nodesGBRT[id].update([time], [cpu])
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

        if myfile:  # 文件存在
            filename = myfile.filename  # 获取文件名

            fullFileName = destFolder + '/' + filename

            myfile.save(destFolder + '/' + filename)  # 保存

            return {"msg": "success", 'filename': filename}, 200
        else:
            return {"msg": "fail, file not exists"}, 400

    def get(self, folder):
        return {'msg': folder}

# 单个任务接口
class RESTComputingTask(Resource):
    def get(self, blk_id):
        pass
    
    def put(self, blk_id):
        
        if computingShareTask == None:
            return {'msg': 'no computing task'}, 400

        blks = computingShareTask.blocks

        args = parser.parse_args()

        if 'status' in args and args['status'] == 'finished' and 'resultName' in args:
            blks[blk_id].status = 'finished'
            blks[blk_id].resultName = args['resultName']

            return {'msg': 'modify ok'}, 200
        else:
            return {'msg': 'args error'}, 400

    


       

# 算力共享平台分发接口，接收参数为程序名和数据包名，其中，程序为单个可执行文件，数据包后缀为tar.gz
class RESTComputingTasks(Resource):
    # 获取任务
    def get(self):

        # 如果没有任务
        if computingShareTask == None:
            return {'msg': 'no computing task'}, 400

        args = parser.parse_args()

        if 'type' in args and args['type'] == 'all': # 如果是访问所有
            blks = computingShareTask.blocks
            data = [ele.toJson() for ele in blks]

            return {'msg': 'success', 'data': data}, 200
        
        else: # 否则取单个任务
            # 通过下标访问任务块，寻找第一个没有被分配的任务
            for i in range(len(blks)):
                if(blks[i].status == 'stop'):
                    blks[i].status = 'running'
                    break

            if i == 0 or i == len(blks):
                return {'msg': 'failed, no tasks remaining'}, 400
            
            data = {
                'blk_id': i, # 下标即为id
                'programName': blks[i].programName,
                'dataName': blks[i].dataName
            }
            # 返回任务

            return {'msg': 'success', 'data': data}, 200

        
    # 分发任务
    def post(self):

        # 检查是否已经有任务在运行，如果有，则返回
        global computingShareTask
        if computingShareTask != None:
            return {'msg': 'there is a task running'}, 400


        try:
            programName = request.form['programName']
            dataName = request.form['dataName']
        except:
            return {'msg': 'arguments illegal'}, 400

        programFullName = PROGRAM_FOLDER + '/' + programName
        dataFullName = DATA_FOLDER + '/' + dataName

        newComputingShareDockerFolder = TEMP_FOLDER + '/' + programName + '_folder'
        if os.path.exists(newComputingShareDockerFolder):
            shutil.rmtree(newComputingShareDockerFolder)
        os.mkdir(newComputingShareDockerFolder)

        shutil.copy(programFullName, newComputingShareDockerFolder + '/cal.py')
        IMAGE_FOLDER = "./image"
        shutil.copy(IMAGE_FOLDER + "/DataProcess.py", newComputingShareDockerFolder + '/DataProcess.py')
        shutil.copy(IMAGE_FOLDER + "/BaseDockerfile", newComputingShareDockerFolder + '/Dockerfile')
        image = ImageBuilder(dockerfile_folder_path=newComputingShareDockerFolder,
                             tag=programName).build()

        try:
            computingShareTask = ComputingShareTask('task001', programFullName, dataFullName, nodesGBRT)
            computingShareTask.run()

            computingShareService = ServiceBuilder(image=image,
                                                   name=programName,
                                                   nodelist=computingShareTask.avaiableNodesList
                                                   )
            # computingTasks.newTask(programFullName, dataFullName, nodesGBRT)  # 新建算力共享任务
        except Exception as e:
            print(e)
            return {'msg': 'failed'}, 400

        return {"msg": "success"}, 200


# 文件管理接口，可以上传和删除
class RESTFiles(Resource):
    # 获取文件
    def get(self, filename):
        return send_from_directory(FILE_FOLDER, filename)

    # 删除文件
    def delete(self, filename):
        try:
            os.remove(FILE_FOLDER + '/' + filename)
        except:
            return {"msg": "file not exists"}, 410
        else:
            return {"msg": "delete success"}, 200
    
    # 上传文件
    def post(self, filename):
        # 从请求体中获得文件
        myfile = request.files['file']

        if myfile:  # 文件存在

            myfile.save(FILE_FOLDER + '/' + filename)  # 保存

            return {"msg": "success", 'filename': filename}, 200
        else:
            return {"msg": "fail, file not exists"}, 400


# docker分发接口.docker文件名从url中解析得到，分发的目标节点id从post接口中得到
class RESTDockerDeploy(Resource):
    def post(self):

        try:
            dockerName = request.form['dockerName']
            num = int(request.form['num'])

            print(dockerName, num)

            dockerFullPath = DOCKER_FOLDER + '/' + dockerName  # 完整docker路径
            newDockerfolder = TEMP_FOLDER + '/' + dockerName + "_folder"

            if os.path.exists(newDockerfolder):
                shutil.rmtree(newDockerfolder)

            os.mkdir(newDockerfolder)

        except Exception as e:
            print(e)
            return {'msg': 'deploy failed'}, 400

        shutil.copy(DOCKER_FOLDER + '/hello', TEMP_FOLDER + '/' + dockerName + "_folder" + "/hello")
        shutil.copy(dockerFullPath, TEMP_FOLDER + '/' + dockerName + "_folder" + "/Dockerfile")
        image = ImageBuilder(newDockerfolder, dockerName).build()
        service = ServiceBuilder(image=image,
                                 name=dockerName,
                                 replicas=num).run()

        print(dockerFullPath)

        return {'msg': 'deploy success'}, 200


# 所有dockersinfo
class RESTDockers(Resource):
    def get(self):
        fileNames = os.listdir(DOCKER_FOLDER)
        fileFullNames = (DOCKER_FOLDER + '/' + fn for fn in fileNames)
        fileSizes = [formatSize(os.path.getsize(ffn)) for ffn in fileFullNames]

        data = [{'name': ele[0], 'size': ele[1]} for ele in zip(fileNames, fileSizes)]

        return {'msg': 'success', 'data': data}, 200


# 获取token
class RESTToken(Resource):
    def get(self):
        try:
            token = client.swarm.attrs['JoinTokens']['Worker']
        except:
            print("token error")
            return {'msg': 'token error'}, 500
        else:
            return {'msg': 'success', 'token': token}, 200


class RESTPredict(Resource):
    def get(self, nodeid):

        # 预测时间序列
        data = [25, 35, 25, 56, 25, 35, 25, 56, 25, 35, 25, 56, 25, 35, 25, 56]

        return {'msg': 'success', 'data': data}, 200
# ==================================================
api = restful.Api(app)
# 接口列表，将/example路由到RESTExample类
api.add_resource(RESTExample, '/example')
# 节点负载信息接口
api.add_resource(RESTNodeInfo, '/nodeinfo')
# 文件上传接口,比如 /upload/docker则是向docker文件夹上传文件，文件名不能与已有文件重复
api.add_resource(RESTUpload, '/upload/<string:folder>')
# 文件管理接口,下载和删除
api.add_resource(RESTFiles, '/files/<path:filename>')
# docker分发接口，比如 /deploy/docker001 ，参数中 nodeIds = [5, 3, 56]，则是向 5, 3, 56分发镜像
api.add_resource(RESTDockerDeploy, '/dockerdeploy')
# 算力共享平台，集合管理接口
api.add_resource(RESTComputingTasks, '/computingtasks')
# 算力共享平台，单个任务管理接口
api.add_resource(RESTComputingTask, '/computingtask/<int:blk_id>')
# docker信息获取
api.add_resource(RESTDockers, '/dockers')
# docker token获取
api.add_resource(RESTToken, '/token')
# 预测序列
api.add_resource(RESTPredict, '/predict/<string:nodeid>')

# ===================================================
# 初始化工作目录
def initWorkSpace():
    # 如果存储文件的文件夹不存在，则创建
    for folder in ALLOWED_FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print("mkdir " + folder + " success!")


# 初始化Docker
def initDocker():
    global client
    try:
        client.swarm.init(advertise_addr="192.168.2.182")
        ##获取worker加入Swarm所需密钥
        workerJoinToken = client.swarm.attrs['JoinTokens']['Worker']
        print(workerJoinToken)
    except Exception as e:
        print(e)


# ===================================================

if __name__ == '__main__':
    SWARM_MANAGER_ADDR = "192.168.1.2:2377"
    # 初始化工作目录
    initWorkSpace()
    # 初始化Swarm
    initDocker()
    # 添加协程
    # threads.append(gevent.spawn(app.run, host="0.0.0.0", port=5000, debug=True))  # flask web服务

    # 等待所有协程结束
    # gevent.joinall(threads)

    app.run(host="0.0.0.0", port=5000, debug=True)
