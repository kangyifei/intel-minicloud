import shutil
import subprocess
import os


class sharedComputing(object):
    def __init__(self,codefile_path,datafolder_path):
                self.codefile_path=codefile_path
                self.datafolder_path=datafolder_path
    def build(self):
        basetxt=""
        dockerfile=open("./temp/Dockerfile","w")
        dockerfile.write(basetxt)
        dockerfile_path=os.getcwd()+"/temp"
        shutil.copy(self.codefile_path,"./temp/cal.py")
        times = 0
        while (times < 3):
            pipe = subprocess.Popen("docker build -f ./temp", shell=True)
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