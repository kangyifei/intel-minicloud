import time
import numpy as np

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.ensemble import RandomForestRegressor


##梯度下降加速决策树
class GBRT(object):

    def __init__(self, n_trees):
        self.est = GradientBoostingRegressor(n_estimators=n_trees, learning_rate=0.1)
        # self.est=RandomForestRegressor(n_estimators=n_trees)
        self._trained = False

    def update(self, time, data):
        time = np.array(time).reshape(-1, 1)
        # data = np.array(data).reshanpe(-1, 1)
        if not self._trained:
            print("first time trained")
            self.est.fit(time, data)
            self._trained = True
        else:
            print("not first time trained")
            self.est.set_params(warm_start=True, n_estimators=self.est.get_params()["n_estimators"] + 10)
            print(self.est.warm_start)
            self.est.fit(time, data)

    def predict(self, time, time_length):
        time = np.array(time).reshape(-1, 1)
        time = time % time_length
        return self.est.predict(time)


if __name__ == '__main__':
    model = GBRT(n_trees=30)
    ##origindata:[1,2,3,4, 5, 6, 7, 8,9,10]
    #############[1,1,1,10,10,10,10,1,1,1]
    print(model.est.get_params()["n_estimators"])
    print(time.time())
    # model.update([1, 2, 3, 4, 5, 6,7, 8, 9, 10], [1, 1, 1, 10, 10, 10,1, 1, 1, 1])

    # for i in range(1,200):
    #     x.append(i)
    #     y.append(2)
    # for i in range(200, 400):
    #     x.append(i)
    #     y.append(10)
    # for i in range(400, 600):
    #     x.append(i)
    #     y.append(2)
    # for i in range(600, 800):
    #     x.append(i)
    #     y.append(10)

    import mat4py
    x = mat4py.loadmat("time.mat")['time']
    y = mat4py.loadmat("cpu.mat")['cpu']
    from sklearn.model_selection import cross_val_score

    model.update(np.array(x).reshape(-1, 1), np.array(y).ravel())
    # score = cross_val_score(model.est, np.array(x).reshape(-1, 1), np.array(y).ravel(), cv=2)
    print(time.time())
    # print(score)
    # print(score.mean())
    # model.update([7, 8, 9, 10], [])
    # print(model.est.get_params()["n_estimators"])
    # # print(time.time())
    # print(model.predict([15]))
    # print(time.time())
    print(model.predict([100001, 100002, 100003, 100004, 100005, 100006]))
    print(model.predict([120001, 120002, 120003, 120004, 120005, 120006]))
    # print(time.time())
    # print(model.est.score(np.array([1001, 1002, 1003, 1004, 1005, 1006]).reshape(-1,1), [1, 1, 1, 10, 10, 10]))
