import subprocess

##直接通过dockerfile构建
class DirectlyDocker(object):

    def __init__(self, dockerfile_path=None):
        self.directly_build = True
        self.dockerfile_path = dockerfile_path

    def build(self):
        times = 0
        while (times < 3):
            pipe = subprocess.Popen("docker build -f " + self.dockerfile_path, shell=True)
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
