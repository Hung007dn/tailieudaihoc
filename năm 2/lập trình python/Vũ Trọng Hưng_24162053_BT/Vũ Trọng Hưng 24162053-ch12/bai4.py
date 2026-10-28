#Vũ Trọng Hưng 24162053
import pandas as pd
import numpy as np

s1 = pd.Series(np.random.randint(1, 5, size=100))
s2 = pd.Series(np.random.randint(1, 4, size=100))
s3 = pd.Series(np.random.randint(10000, 30001, size=100))

df = pd.concat([s1, s2, s3], axis=1)
df.columns = ['bedrs', 'bathrs', 'price_sqr_meter']

bigcolumn = pd.concat([s1, s2, s3], axis=0)
df_big = pd.DataFrame(bigcolumn, columns=['bigcolumn'])

df_big = df_big.reset_index(drop=True)
df_big.index = range(300)
print(df_big)