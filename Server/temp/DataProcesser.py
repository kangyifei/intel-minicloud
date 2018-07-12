import requests
import os
import logging
import json

BASE_URL = 'http://127.0.0.1:5000'

WORK_DIR = './temp'

FILE_NAME_BASE = 'res'

class DataProcesser():

    def __init__(self) -> None:
        super().__init__()
        # 如果工作目录不存在，则新建
        if not os.path.exists(WORK_DIR): 
            os.makedirs(WORK_DIR)
        
    # 输入数据接口，首先请求数据，返回本地文件名
    def input_data(self):
        ##TODO:添加get要处理的数据文件路径的服务器端响应
        # 拼接获取任务的url
        getTaskDataUrl = BASE_URL + '/'
        # 从服务器获取数据文件名称
        try:
            r = requests.get(getTaskDataUrl).text
            res = json.loads(r)

            taskDataFileName = res['fileName']
            taskID = res['taskID']
            # 下载该文件
            fileUrl = BASE_URL + '/files/data/' + taskDataFileName
            localFileName = WORK_DIR + '/' + taskDataFileName

            if os.path.exists(localFileName):
                os.remove(localFileName)

            self.download(fileUrl, localFileName)
        except:
            return None

        if os.path.exists(localFileName):
            return localFileName, taskID
        else:
            return None
    
    # 输出文件接口
    def output_data(self, fileFullName, taskID):
        pass       

    # 自动保存文件
    def saveFile(self, data):
        for i in range(1000):
            # 生成全名
            fileFullName = WORK_DIR + '/' + FILE_NAME_BASE + '_' + str(i)
            # 如果该文件不存在，则创建结果文件，并写入
            if not os.path.exists(fileFullName):
                with open(fileFullName) as res:
                    res.write(data)
                return fileFullName # 返回该名字

        return None

    # 文件上传，同步方法
    def upload(self, url, localFileFullName, remoteFileName, callback = lambda : logging.debug("upload success")):
        files = {
            'file': open(localFileFullName, 'rb')
        }

        data = {'enctype':'multipart/form-data'}

        r = requests.post(url, data=data, files=files)

        if r.status_code == 200:
            callback()

    # 文件下载, 同步方法
    def download(self, url, fileFullName, callback = lambda : logging.debug("download success")):
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