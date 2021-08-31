import pandas as pd

df = pd.read_csv('C:/Users/kyujin/Desktop/PROCESS/crawling_result_kids.csv')
keywords = list(set(df['키워드']))

set_list = []
non_set_list = []
for keyword in keywords:
    for i in range(len(keywords)):
        if '상하' in keyword:
            set_list.append(keyword)
        elif '세트' in keyword:
            set_list.append(keyword)
        else:
            non_set_list.append(keyword)

set_keyword = list(set(set_list))
non_set_keyword = list(set(non_set_list))

print((set_keyword))
print(len(set_keyword))



