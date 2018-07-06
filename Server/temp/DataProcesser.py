import requests

def input_data():
    f=open("\HOME\DATA","r")
    return f
def output_data(res):
    BASE_URL = 'http://127.0.0.1:5000'
    info={
        "id": 1,
        "res":res
    }
    status = requests.post(BASE_URL + '/calres', info)
    print(status.text)