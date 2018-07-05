import subprocess
import docker


##直接通过dockerfile构建
class DirectlyDockerBuilder(object):
    client = docker.from_env()

    def __init__(self, dockerfile_folder_path=None):
        self.directly_build = True
        self.dockerfile_folder_path = dockerfile_folder_path

    def build(self):
            image, log = self.client.images.build(path=self.dockerfile_folder_path)
            return image
