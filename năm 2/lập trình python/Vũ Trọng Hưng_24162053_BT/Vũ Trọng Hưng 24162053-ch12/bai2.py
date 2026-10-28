#Vũ Trọng Hưng 24162053
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('chipotle.tsv', sep='\t')

df['item_price'] = df['item_price'].str.replace('$', '').astype(float)

filtered = df[df['item_price'] > 10]
unique_items = filtered.drop_duplicates(subset='item_name')
print(unique_items[['item_name', 'item_price']])

sorted_items = unique_items.sort_values('item_name')
print(sorted_items[['item_name', 'item_price']])

max_price_item = unique_items.loc[unique_items['item_price'].idxmax()]
print(max_price_item)

veggie_orders = df[df['item_name'] == 'Veggie Salad Bowl']
order_count = veggie_orders['order_id'].nunique()
total_quantity = veggie_orders['quantity'].sum()
print(f"Veggie Salad Bowl xuất hiện trong {order_count} đơn hàng với tổng số lượng {total_quantity}")

top_items = df.groupby('item_name')['quantity'].sum().sort_values(ascending=False).head(5)
top_items.plot(kind='bar', color='lightgreen')
plt.title('Top 5 sản phẩm được mua nhiều nhất')
plt.xlabel('Tên sản phẩm')
plt.ylabel('Tần suất mua')
plt.tight_layout()
plt.show()

order_quantities = df.groupby('order_id')['quantity'].sum()
plt.scatter(order_quantities.index, order_quantities.values, color='orange')
plt.title('Số lượng mặt hàng trên mỗi đơn hàng')
plt.xlabel('Mã đơn hàng')
plt.ylabel('Tổng số lượng')
plt.tight_layout()
plt.show()