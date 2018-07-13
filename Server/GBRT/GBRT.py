import time
import numpy as np

from sklearn.ensemble import GradientBoostingRegressor


##梯度下降加速决策树
class GBRT(object):

    def __init__(self, n_trees):
        self.est = GradientBoostingRegressor(n_estimators=n_trees,loss='ld')
        self._trained=False
    def update(self, time, data):
        time = np.array(time).reshape(-1, 1)
        # data = np.array(data).reshape(-1, 1)
        if not self._trained:
            print("first time trained")
            self.est.fit(time, data)
            self._trained = True
        else:
            print("not first time trained")
            self.est.set_params(warm_start=True, n_estimators=self.est.get_params()["n_estimators"]+1)
            print(self.est.warm_start)
            self.est.fit(time, data)

    def predict(self, time):
        time = np.array(time).reshape(-1, 1)
        return self.est.predict(time)


if __name__ == '__main__':
    model = GBRT(n_trees=1000)
    ##origindata:[1,2,3,4, 5, 6, 7, 8,9,10]
    #############[1,1,1,10,10,10,10,1,1,1]
    print(model.est.get_params()["n_estimators"])
    print(time.time())
    # model.update([1, 2, 3, 4, 5, 6,7, 8, 9, 10], [1, 1, 1, 10, 10, 10,1, 1, 1, 1])
    x=[]
    y=[]
    for i in range(1,200):
        x.append(i)
        y.append(2)
    for i in range(200, 400):
        x.append(i)
        y.append(10)
    for i in range(400, 600):
        x.append(i)
        y.append(2)
    for i in range(600, 800):
        x.append(i)
        y.append(10)
    model.update(x,y)
    print(time.time())
    # model.update([7, 8, 9, 10], [])
    # print(model.est.get_params()["n_estimators"])
    # # print(time.time())
    # print(model.predict([15]))
    # print(time.time())
    print(model.predict([801, 802, 803, 804, 805, 806]))
    print(model.predict([1001, 1002, 1003, 1004, 1005, 1006]))
    # print(time.time())
    print(model.est.score(np.array([1001, 1002, 1003, 1004, 1005, 1006]).reshape(-1,1), [1, 1, 1, 10, 10, 10]))
