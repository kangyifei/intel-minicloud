import subprocess
import docker


##直接通过dockerfile构建
##传入的dockerfile_folder_path应为dockerfile所在文件夹
class ImageBuilder(object):
    client = docker.from_env()

    def __init__(self, dockerfile_folder_path,tag):
        self.__dockerfile_folder_path = dockerfile_folder_path
        self.__tag=tag
    def build(self):
            image, log = self.client.images.build(path=self.__dockerfile_folder_path,tag=self.__tag)
            return image
