#Vũ Trọng Hưng 24162053
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('ChurnCustomer.csv', header=0, index_col='RowNumber')
print(df.describe(include='all'))

credit_by_geo = df.groupby('Geography')['CreditScore'].mean()
print(credit_by_geo)

df['AgeGroup'] = pd.qcut(df['Age'], q=5, labels=['Nhóm 1', 'Nhóm 2', 'Nhóm 3', 'Nhóm 4', 'Nhóm 5'])

age_counts = df['AgeGroup'].value_counts().sort_index()
age_counts.plot(kind='bar', color='skyblue')
plt.title('Số lượng khách hàng theo nhóm độ tuổi')
plt.xlabel('Nhóm độ tuổi')
plt.ylabel('Số lượng khách hàng')
plt.tight_layout()
plt.show()