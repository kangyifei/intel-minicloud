import shutil
import subprocess
import os


##构建共享算力镜像
# TODO:写共享算力镜像的基础镜像Dockerfile
class sharedComputingBuilder(object):
    def __init__(self, codefile_path, datafolder_path):
        self.codefile_path = codefile_path
        self.datafolder_path = datafolder_path

    def build(self):
        shutil.copy("./BaseDockerfile", "./temp/Dockerfile")
        dockerfile_folder_path = os.getcwd() + "/temp"
        shutil.copy(self.codefile_path, "./temp/cal.py")
        image, log = self.client.images.build(path=dockerfile_folder_path)
        return image
