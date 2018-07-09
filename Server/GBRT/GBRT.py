import time
import numpy as np

from sklearn.ensemble import GradientBoostingRegressor


##梯度下降加速决策树
##TODO：验证WarmStart不会重置模型
class GBRT(object):
    _trained = False

    def __init__(self, n_trees):
        self.est = GradientBoostingRegressor(n_estimators=n_trees)

    def update(self, time, data):
        time = np.array(time).reshape(-1, 1)
        # data = np.array(data).reshape(-1, 1)
        if self._trained:
            print("first time trained")
            self.est.fit(time, data)
            self._trained = True
        else:
            print("not first time trained")
            self.est.set_params(warm_start=True)
            print(self.est.warm_start)
            self.est.fit(time, data)

    def predict(self, time):
        time=np.array(time).reshape(-1,1)
        return self.est.predict(time)


if __name__ == '__main__':
    model = GBRT(n_trees=10)
    ##origindata:[1,2,3,4, 5, 6, 7, 8,9,10]
    #############[1,1,1,10,10,10,10,1,1,1]
    print(time.time())
    model.update([1, 2, 3, 4, 5, 6], [1, 1, 1, 10, 1, 1])
    print(time.time())
    model.update([7, 8, 9, 10 ], [10, 1, 1, 1])
    print(time.time())
    print(model.predict([15]))
    print(time.time())
    print(model.predict([7]))
    print(time.time())
