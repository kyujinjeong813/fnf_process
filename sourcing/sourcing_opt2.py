import pandas as pd
import numpy as np

n = 16
R = pd.Series([1 for i in range(n)])
Cost = pd.Series([20511, 20138, 17502, 17502,19031, 17643, 16248, 16248, 17643, 16248, 18833, 19185, 17777, 16479, 17788, 16479])
LT = pd.Series([113, 116, 92, 113, 106, 124, 81, 103, 110, 89, 95, 99, 113, 103, 85, 89])

covmat = np.ones((n,n))

def cost_objective(x):
    ttl_cost = x@Cost.T
    return(ttl_cost)


# 제약함수 : 총 수량 x.sum()이 5만장
def qty_constraint(x):
    return(x.sum()-50000)

def MinVol(covmat, lb, ub):
    x0 = np.repeat(1/covmat.shape[1], covmat.shape[1])
    lbound = np.repeat(lb, covmat.shape[1])
    ubound = np.repeat(ub, covmat.shape[1])
    bnds = tuple(zip(lbound, ubound))

    constraints = ({'type':'eq', 'fun':qty_constraint})
    options = {'ftol':1e-20, 'maxiter':800}

    result = minimize(fun = cost_objective,
                      x0=x0, method='SLSQP',
                      constraints=constraints,
                      options=options,
                      bounds = bnds)
    result(result.x)

# 중국 수량 x[:10].sum()
# 한국 수량 x[10:].sum()