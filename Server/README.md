# MiniCloud后端
## 简介
MiniCloud后端，提供RESTful接口，与前端网页进行交互。
其中app.py是程序的入口文件，REST.py是接口文件

## 使用方法
电脑应安装有python3,pip3,virtualenv(可选)
在虚拟环境下 执行 pip3 install -r requirements.txt，安装依赖
然后python3 app.py执行

使用 curl 或者浏览器访问 ip:5000 即可

## 接口列表
1. /example
* GET /example
参数： 无
返回： {'msg': 'ok'}
* POST /example
参数： 无
返回： HTTP状态码400