from .DataProcesser import input_data,output_data
import numpy as np
if __name__ == '__main__':
    f=input_data()
    # f = open(".\DATA", "r")
    i=int(f.readline())
    print(i)
    martix=[]
    for k in range(i):
        print(k)
        m=f.readline()
        martix.append(np.mat(m))
    print(martix)
    res=1
    for k in range(i):
        res=np.multiply(res,martix[k])
    output_data(res)
