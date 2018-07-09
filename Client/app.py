import shutil
import sys
import docker
import psutil
import time
import requests

BASE_URL = 'http://127.0.0.1:5000'
MANAGER_ADDR="192.168.1.145:2377"
JOIN_TOKEN=""
if __name__ == '__main__':
    client = docker.from_env()
    if not client.swarm.join(remote_addrs=[MANAGER_ADDR],join_token=JOIN_TOKEN):
        sys.exit("swarm init failed")
    while (1):
        info = {
            'id': client.info()['Swarm']['NodeID'],
            'time':int(time.time()),
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'hdd': psutil.disk_usage("/").percent
        }

        # 向服务器发送消息
        status = requests.post(BASE_URL + '/nodeinfo', info)

        print(status.text)

        time.sleep(5)
