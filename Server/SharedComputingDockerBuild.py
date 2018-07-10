import shutil
import subprocess
import os


##构建共享算力镜像
# TODO:写共享算力镜像的基础镜像Dockerfile
class sharedComputingBuilder(object):
    def __init__(self, codefile_path, datafolder_path, tag):
        self.codefile_path = codefile_path
        self.datafolder_path = datafolder_path
        self.tag = tag

    def build(self):
        shutil.copy("./BaseDockerfile", "./image/Dockerfile")
        dockerfile_folder_path = os.getcwd() + "/image"
        shutil.copy(self.codefile_path, "./image/cal.py")
        image, log = self.client.images.build(path=dockerfile_folder_path, tag=self.tag)
        return image
