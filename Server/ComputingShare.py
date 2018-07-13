
import os
import tarfile
import time



class ComputingShareTask(object):
    # 内部block类，任务细分块
    class Block():
        def __init__(self, programName, dataName, blk_id):
            self.programName = programName
            self.dataName = dataName
            self.blk_id = blk_id # 任务块id
            self.status = 'stop' # 分为stop还未开始 processing 正在处理 和 finished 已完成 四种状态

    def __init__(self, id, programName, dataName,nodesGBRT): # 任务id,任务块数
        self.id = id
        self.status = 'stop' 
        self.blocks = [] # 任务划分块
        self.programName=programName
        self.nodesGBRT=nodesGBRT
        self.dataName=dataName
        self.dataFileList = []

    ##获取可用节点列表方法，传入任务的运行时间和CPU最高占用率
    def __getAvaiableNodes(self,runningTime,cpuPeakUsage):
        nodesGBRT=self.nodesGBRT
        avaiableNodesList=[]
        for id,GBRT in nodesGBRT.items():
            timenow=int(time.time())
            timeend=timenow+runningTime
            timelist=range(timenow,timeend,5)
            avaiable=True
            for timedot in timelist:
                cpuUsage=GBRT.predict(timedot)
                if not 100-cpuUsage>cpuPeakUsage:
                    avaiable=False
                    break
            if avaiable:
                avaiableNodesList.append(id)


    ##解压缩tar文件方法
    def __untar(self,file_name):
        tar = tarfile.open(file_name)
        names = tar.getnames()
        if os.path.isdir(file_name + "_files"):
            pass
        else:
            os.mkdir(file_name + "_files")
            #因为解压后是很多文件，预先建立同名目录

        for name in names:
            tar.extract(name, file_name + "_files/")

        tar.close()

    ##解压缩数据包，返回每个数据文件完整路径列表
    def __utarData(self):
        self.__untar(self.dataName)
        path, folders, files = os.walk(self.dataName + "_files")
        dataFileList = []
        for file in files:
            dataFileList.append(self.dataName + "_files/" + file)
        return  dataFileList

    # 启动
    def run(self):
        self.dataFileList = self.__untar(self.dataName)

        blk_id = 0
        # 添加任务到 blocks列表里
        for file in self.dataFileList:
            self.blocks.append(self.Block(self.programName, file, blk_id))
            blk_id += 1 # blk_id自增，与block在self.blocks[]中的位置索引相同

        self.avaiableNodesList = self.__getAvaiableNodes(600, 30)




class ComputingShareTasks(object):
    def __init__(self):
        self.taskid = 0
        self.tasks = []

    def newTask(self, programName, dataName,nodesGBRT):
        task = ComputingShareTask(self.taskid, programName, dataName,nodesGBRT)

