#Vũ Trọng Hưng 24162053
import pandas as pd

df = pd.read_csv('wind.data', sep='\s+', parse_dates=[[0, 1, 2]])
df.columns = ['Yr_Mo_Dy'] + list(df.columns[1:])
df.set_index('Yr_Mo_Dy', inplace=True)

count_missing = df.isnull().sum()
count_present = df.count()
print("Số giá trị hiện có:")
print(count_present)
print("\nSố giá trị thiếu:")
print(count_missing)

mean_wind_speed = df.mean().mean()
print(f"\nTốc độ gió trung bình toàn bộ dữ liệu: {mean_wind_speed:.2f}")

loc_stats = df.describe().T[['min', 'max', 'mean', 'std']]
print("\nThống kê tốc độ gió tại mỗi vị trí:")
print(loc_stats)

january_avg = df[df.index.month == 1].mean()
print("\nTốc độ gió trung bình trong tháng 1 tại mỗi nơi:")
print(january_avg)

yearly = df.resample('Y').mean()
monthly = df.resample('M').mean()
weekly = df.resample('W').mean()

print("\nThống kê theo năm:")
print(yearly)
print("\nThống kê theo tháng:")
print(monthly)
print("\nThống kê theo tuần:")
print(weekly)