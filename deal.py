import pandas as pd
import csv

df = pd.read_csv('dashuju3.csv', encoding='utf-8')
df1 = df.drop_duplicates(subset=None)
print('去重前数据框的长度为：', len(df), '\n', '去重后数据框的长度为：', len(df1))
df1.to_csv('dashuju31.csv')
