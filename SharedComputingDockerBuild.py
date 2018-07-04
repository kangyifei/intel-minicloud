import shutil
import subprocess
import os

##构建共享算力镜像
#TODO:写共享算力镜像的基础镜像Dockerfile
class sharedComputing(object):
    def __init__(self,codefile_path,datafolder_path):
                self.codefile_path=codefile_path
                self.datafolder_path=datafolder_path
    def build(self):
        shutil.copy("./BaseDockerfile","./temp/Dockerfile")
        dockerfile_path=os.getcwd()+"/temp"
        shutil.copy(self.codefile_path,"./temp/cal.py")
        times = 0
        while (times < 3):
            pipe = subprocess.Popen("docker build ./temp", shell=True)
            pipe.wait()
            res = pipe.stdout.readlines()
            for line in res:
                i = line.find("Successfully built")
                if (i!=-1):
                    return line.split(" ")[2]
            times += 1
        if (times == 3):
            print("build error")
            return 0