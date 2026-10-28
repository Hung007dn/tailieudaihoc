#Vũ Trọng Hưng 24162053
import pandas as pd

df = pd.read_csv('u.user', sep='|')

avg_age_by_job = df.groupby('occupation')['age'].mean()
print("Độ tuổi trung bình theo nghề nghiệp:")
print(avg_age_by_job)

male_ratio_by_job = df[df['gender'] == 'M'].groupby('occupation')['gender'].count() / df.groupby('occupation')['gender'].count()
male_ratio_sorted = male_ratio_by_job.sort_values(ascending=False)
print("\nTỷ lệ nam theo nghề nghiệp (giảm dần):")
print(male_ratio_sorted)

min_max_age_by_job = df.groupby('occupation')['age'].agg(['min', 'max'])
print("\nTuổi nhỏ nhất và lớn nhất theo nghề nghiệp:")
print(min_max_age_by_job)

avg_age_by_job_gender = df.groupby(['occupation', 'gender'])['age'].mean()
print("\nTuổi trung bình theo tổ hợp nghề nghiệp – giới tính:")
print(avg_age_by_job_gender)

gender_counts = df.groupby(['occupation', 'gender'])['gender'].count().unstack()
gender_percent = gender_counts.div(gender_counts.sum(axis=1), axis=0) * 100
print("\nTỷ lệ phần trăm nam – nữ theo nghề nghiệp:")
print(gender_percent)