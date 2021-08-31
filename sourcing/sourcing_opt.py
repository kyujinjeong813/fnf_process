import numpy as np
import pandas as pd

# 주어지는 것
# 1. 각 루트에 대한 cost, leadtime >> DataFrame 형태
# 2. 총 order qty
# 3. 주차별 sales 예상
# 4. 안전재고 또는 목표 재고주수
# 4. 오더 시점의 기초재고
# 참고참고 https://developers.google.com/optimization/cp/integer_opt_cp

init_stock = 3000
order_qty = 20000
min_stock = 2000
weekly_sales = 1000

df = pd.DataFrame({'route':['r1', 'r2', 'r3', 'r4'],
                   'cost':[100, 85, 70, 65],
                   'leadtime':[4,6,8,9]})

leadtime_list = df['leadtime'].to_list()
m = max(leadtime_list)
n = min(leadtime_list)
r = len(df['route'])

for i in range(m):
    if i < n:
        rcv = 0
    stock = init_stock - weekly_sales*(i+1) + rcv
    while stock >= min_stock:
# 으아니야아 이거아니야
# http: // egloos.zum.com / incredible / v / 7473314
# https://realpython.com/python-scipy-cluster-optimize/
# https://wikidocs.net/15656

# 재고를 간단히 한(?) 함수를 일단 작성합시당
from scipy.optimize import minimize_scalar, LinearConstraint, NonlinearConstraint

# x = 각 루트 별 발주 수량 배열, y = cost (df['cost'].array)

x = np.eye(r)[0]*order_qty
cost = df['cost']

def objective_function(x, cost):
    return x.dot(cost)

constraint = LinearConstraint(np.ones(n_buyers), lb=n_shares, ub=n_shares)
# NonlinearConstraint
bounds = [(0,n) for n in n_shares_per_buyer]

res = minimize(objective_function,
               x0=10, args=(y,),
               constraints=contraint,
               bounds=bounds)