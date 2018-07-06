import sys
import TcpClient
import docker
import psutil
import time
import requests

BASE_URL = 'http://127.0.0.1:5000'

if __name__ == '__main__':
    # client=docker.from_env()
    # if not client.swarm.join(remote_addrs=["192.168.1.145:2377"]):
    #     sys.exit("swarm init failed")
    # tcp_client=TcpClient.TcpClient("192.168.1.145","5321")
    # tcp_client.run()
    while(1):
        # tcp_client.send({"cpu":psutil.cpu_percent(interval=1)})

        info = {
            'id': 1,
            'cpu': 23.5,
            'memory': 256,
            'hdd': 25.6
        }

        # 向服务器发送消息
        status = requests.post(BASE_URL + '/nodeinfo', info)

        print(status.text)

        time.sleep(1)