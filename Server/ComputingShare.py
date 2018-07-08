class ComputingShareTask():
    # 内部block类，任务细分块
    class block():
        def __init__(self, programName, dataName):
            self.programName = programName
            self.dataName = dataName
            self.status = 'stop' # 分为stop还未开始 processing 正在处理 和 finished 已完成 四种状态

    def __init__(self, id, programName, dataName): # 任务id,任务块数
        self.id = id
        self.status = 'stop' 
        self.blocks = [] # 任务划分块

        # 解压缩data

        lenData = 2 # 解压缩后data数目






class ComputingShareTasks():
    def __init__(self):
        self.taskid = 0
        self.tasks = []
    
    def newTask(self, programName, dataName):
        task = ComputingShareTask(self.taskid, programName, dataName)
        self.taskid += 1
        self.tasks.append(task)