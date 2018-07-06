import subprocess
import docker


##直接通过dockerfile构建
##传入的dockerfile_folder_path应为dockerfile所在文件夹
class DirectlyDockerBuilder(object):
    client = docker.from_env()

    def __init__(self, dockerfile_folder_path,tag):
        self.directly_build = True
        self.dockerfile_folder_path = dockerfile_folder_path
        self.tag=tag
    def build(self):
            image, log = self.client.images.build(path=self.dockerfile_folder_path,tag=self.tag)
            return image
