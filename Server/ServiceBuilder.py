import docker
import docker.types


class ServiceBuilder(object):
    def __init__(self, image, name, nodelist=None, replicas=2):
        self.__image = image.tags[0]
        self.__name = name.replace(".","")
        self.__nodelist = nodelist
        self.__replicas = replicas

    def run(self):
        client = docker.from_env()
        if self.__nodelist is None:
            client.services.create(image=self.__image,
                                   name=self.__name,
                                   mode=docker.types.ServiceMode
                                   (mode="replicated", replicas=int(self.__replicas)),
                                   endpoint_spec=docker.types.EndpointSpec(mode='vip', ports={8010: 8000}))

        else:
            for nodeid in self.__nodelist:
                node = client.nodes.get(node_id=nodeid)
                node.update({'Availability': 'active',
                 'Name':node.attrs['Description']['Hostname'],
                 'Role': node.attrs['Spec']['Role'],
                 'Labels': {self.__name: self.__name}
                })
            client.services.create(image=self.__image,
                                   name=self.__name,
                                   constraints=["node.labels." + self.__name + "==" + self.__name],
                                   mode=docker.types.ServiceMode
                                   (mode="replicated", replicas=int(len(self.__nodelist))),)