from DataProcesser import DataProcesser
import numpy as np
import time

# 字符串转矩阵，如'1 2;3 4'，转为[[1,2],[3,4]]
def str2mat(istr):
    # 通过;将字符串分割
    rows = istr.split(';')
    # 通过空格分割每行，转化为二维列表
    mat = [row.split(' ') for row in rows]
    # 字符转数字
    mat = [[int(ele) for ele in row] for row in mat]
    # 转化为np矩阵
    return np.array(mat)


if __name__ == '__main__':
    dp = DataProcesser()

    # 循环获取
    while True:
        # 读取文件名
        fileName, taskID = dp.input_data()

        # 如果有数据
        if fileName:
            # 打开文件，读取内容
            with open(fileName, 'r') as infile:
                lines = infile.readlines()
            
            # 获取两个矩阵
            mat0 = str2mat(lines[0])
            mat1 = str2mat(lines[1])

            # 相乘
            res = np.multiply(mat0, mat1)

            # 保存，文件名由系统分配
            fileFullName = dp.saveFile(res)

            # 输出该文件
            dp.output_data(fileFullName, taskID)
        else:
            time.sleep(2) # 每两秒钟检查一次