from sklearn.ensemble import GradientBoostingRegressor
##梯度下降加速决策树
##TODO：验证WarmStart不会重置模型
class GBRT(object):
    trained=False
    def __init__(self,n_trees):
        self.est=GradientBoostingRegressor(n_estimators=n_trees)

    def update(self,time,data):
       if self.trained:
            self.est.fit()
            self.trained=True
       else:
           self.est.set_params(warm_start=True)
           self.est.fit(time,data)
    def predict(self,time):
        return self.est.predict(time)

