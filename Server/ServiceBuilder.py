import docker
import docker.types


class ServiceBuilder(object):
    def __init__(self, image, name, nodelist=None, replicas=2):
        self.__image = image
        self.__name = name
        self.__nodelist = nodelist
        self.__replicas = replicas

    def run(self):
        client = docker.from_env()
        if self.__nodelist is None:
            client.services.create(image=self.__image,
                                   name=self.__name,
                                   mode=docker.types.ServiceMode
                                   (mode="replicated", replicas=int(self.__replicas)))
        else:
            for nodeid in self.__nodelist:
                node = client.nodes.get(node_id=nodeid)
                node.update({'Labels': {self.__name: self.__name}})
            client.services.create(image=self.__image,
                                   name=self.__name,
                                   constrains=["node.lables." + self.__name + "==" + self.__name],
                                   mode=docker.types.ServiceMode
                                   (mode="global"))
