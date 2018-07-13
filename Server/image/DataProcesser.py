import requests
import os
import logging
import json

BASE_URL = 'http://192.168.2.182:5000'

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
        getTaskDataUrl = BASE_URL + '/computingtasks'
        # 从服务器获取数据文件名称
        try:
            r = requests.get(getTaskDataUrl).text

            res = json.loads(r)

            dataName = res['data']['dataName'].strip('./files/')
            blk_id = res['data']['blk_id']

            print(dataName)
            # 下载该文件
            fileUrl = BASE_URL + '/files/' + dataName
            localFileName = WORK_DIR + '/' + dataName.split('/')[-1]

            if os.path.exists(localFileName):
                os.remove(localFileName)

            self.download(fileUrl, localFileName)
        except Exception as e:

            print(e)
            return None,None

        if os.path.exists(localFileName):
            return localFileName, blk_id
        else:
            return None,None
    
    # 输出文件接口
    def output_data(self, fileFullName, blk_id):
        resultName = fileFullName.split('/')[-1]
        uploadUrl = BASE_URL + '/files/result/' + resultName 

        self.upload(uploadUrl, fileFullName)

        resUrl = BASE_URL + '/computingtask/' + str(blk_id)
        r = requests.put(resUrl, {'status': 'finished', 'resultName': resultName})

        


    # 自动保存文件
    def saveFile(self, data):
        print(data)
        for i in range(1000):
            # 生成全名
            fileFullName = WORK_DIR + '/' + FILE_NAME_BASE + '_' + str(i)
            # 如果该文件不存在，则创建结果文件，并写入
            if not os.path.exists(fileFullName):
                with open(fileFullName, 'w') as res:
                    res.write(data)
                return fileFullName # 返回该名字

        return None

    # 文件上传，同步方法
    def upload(self, url, localFileFullName, remoteFileName = '', callback = lambda : logging.debug("upload success")):
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