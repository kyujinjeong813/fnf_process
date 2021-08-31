import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_excel('C:/Users/kyujin/Desktop/PROCESS/overall/data_test.xlsx', sheet_name='Sheet1')
print(data.head())

si = len(data.index)
x = np.arange(len(data.index))
y = data['Value1']

plt.figure()
plt.title("alpha=0.4 ES")
plt.plot(x, y)

alpha = 0.4
S = np.zeros(si+50)
x = np.arange(0, si+50)
y = np.zeros(si+50)
for i in range(si + 50):
    if i >= si:
        y[i-1] = data['Value'][si-1]
    else:
        y[i-1] = data['Value'][i]

S[0] = y[0]
for i in range(si+50):
    if i>0:
        S[i] = (1 - alpha) * S[i-1] + alpha*y[i-1]
plt.plot(x,S)

plt.show()