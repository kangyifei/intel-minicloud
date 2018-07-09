import requests
class DataProcesser:

    def __init__(self) -> None:
        super().__init__()

    def input_data(self):
        ##TODO:添加get要处理的数据文件路径的服务器端响应
        BASE_URL = 'http://127.0.0.1:5000'
        res=requests.get(BASE_URL)
        f=open(res.text,"r")
        self.link=res.text
        return f
    def output_data(self,res):
        BASE_URL = 'http://127.0.0.1:5000'
        info={
            "id": self.link,
            "res":res
        }
        status = requests.post(BASE_URL + '/calres', info)
        print(status.text)