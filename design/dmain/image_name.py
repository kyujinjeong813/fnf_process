import os
import pandas as pd

original_dir = 'C:/Users/kyujin/PycharmProjects/design/test/original/'

original_lst = os.listdir(original_dir)
df_result = pd.DataFrame(columns={'file_name', 'partcode', 'color'})

for file in original_lst:
    file_name = file
    rev_name = file_name.replace('-', '_').split('.')[0]
    partcode, colorcode = rev_name.split('_')

    row = {'file_name': file_name, 'partcode': partcode, 'color': colorcode}
    df_result = df_result.append(row, ignore_index=True)

df_result = df_result[['file_name', 'partcode', 'color']]
print(df_result)