from gevent import monkey;monkey.patch_all()
import shutil
import sys
import docker
import psutil
import time
import requests
import gevent
import os
import logging
import requests

FILE_FOLDER = './files'  # 上传文件目录
DOCKER_FOLDER = FILE_FOLDER + '/docker' # docker文件存储目录
PROGRAM_FOLDER = FILE_FOLDER + '/program' # 程序上传目录
DATA_FOLDER = FILE_FOLDER + '/data' # 数据上传目录
RESULT_FOLDER = FILE_FOLDER + '/result' # 结果上传目录
ALLOWED_FOLDERS = [DOCKER_FOLDER, PROGRAM_FOLDER, DATA_FOLDER, RESULT_FOLDER] # 所有允许上传和文件目录集合

BASE_URL = 'http://127.0.0.1:5000'
MANAGER_ADDR="192.168.1.145:2377"

JOIN_TOKEN=""

tasks = [] #任务列表

# 工作协程
# -----------------------------------------------------------------------
# 节点信息上传协程
def infoUploadTask(client):
    while (1):
        info = {
            'id': client.info()['Swarm']['NodeID'],
            'time':int(time.time()),
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'hdd': psutil.disk_usage("/").percent
        }

        # 向服务器发送消息
        status = requests.post(BASE_URL + '/nodeinfo', info)

        logging.debug(status.text)

        gevent.sleep(5)

# 持续检查服务器是否分发了docker，如果有，则下载
def getDocker():
    while(1):
        gevent.sleep(2) # 每2s检查一次
        logging.debug('check docker...')

# 持续检查服务器是否分发了算力共享任务，如果有，则下载
def getComputingTask():
    while(1):
        gevent.sleep(2) # 每2s检查一次
        logging.debug('check computing share...')

# -------------------------------------------------------------------------------------------
# 文件下载, 同步方法
def download(url, fileFullName, callback = lambda : logging.debug("download success")):
    r = requests.get(url)

    if os.path.exists(fileFullName):
        logging.error('file exists!')
        return False

    # 写入文件
    with open(fileFullName, 'wb') as outfile:
        outfile.write(r.content)
    
    logging.info('download success')
    # 执行回调
    callback()

# 异步下载任务
def downloadAsync(url, fileFullName, callback = lambda : logging.debug("download success")):
    # 创建异步下载任务
    dTask = gevent.spawn(download, url, fileFullName, callback)

    tasks.append(dTask)

# 初始化工作目录
def initWorkSpace():
    # 如果存储文件的文件夹不存在，则创建
    for folder in ALLOWED_FOLDERS:
        if not os.path.exists(folder):
            os.makedirs(folder)
            logging.debug("mkdir " + folder + " success!")

# 初始化docker
def initDocker():
    # 初始化docker
    client = docker.from_env()
    if not client.swarm.join(remote_addrs=[MANAGER_ADDR],join_token=JOIN_TOKEN):
        sys.exit("swarm init failed")

    return client

# ================================================
if __name__ == '__main__':

    # 设置日志级别
    logging.basicConfig(level=logging.NOTSET)  

    # 初始化工作目录
    initWorkSpace()

    # 异步下载范例， 下载成功后执行callback回调
    downloadAsync(url = 'http://127.0.0.1:5000/files/docker/app.py', fileFullName = './files/docker/app.py', callback= lambda: print('hello'))
    
    # # 初始化docker
    # client = initDocker()
    
    # # 创建多任务
    # tasks.append(gevent.spawn(infoUploadTask, client)) # 添加 节点信息上传任务 
    # tasks.append(gevent.spawn(getDocker))
    # tasks.append(gevent.spawn(getComputingTask))
    
    # # 阻塞，直到所有协程结束
    gevent.joinall(tasks) 
    