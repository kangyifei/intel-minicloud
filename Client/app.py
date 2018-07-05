import sys
import TcpClient
import docker
import psutil
if __name__ == '__main__':
    client=docker.from_env()
    if not client.swarm.join(remote_addrs=["192.168.1.145:2377"]):
        sys.exit("swarm init failed")
    tcp_client=TcpClient.TcpClient("192.168.1.145","5321")
    tcp_client.run()
    while(1):
        tcp_client.send({"cpu":psutil.cpu_percent(interval=1)})