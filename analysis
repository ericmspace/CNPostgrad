import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Simsun']  # Windows系统
file_path = './result.csv'
data = pd.read_csv(file_path)
# 清洗“所在地”列，提取城市或省份名称
# 正则表达式：先匹配括号中的数字（不保留），然后匹配并保留括号外的中文字符
data['所在地'] = data['所在地'].str.extract(r'\((\d+)\)([\u4e00-\u9fa5]+)')[1]
# 统计每个地区的条目数量
location_counts = data['所在地'].value_counts()
plt.figure(figsize=(10, 8))
location_counts.plot(kind='bar', color='skyblue')
plt.title('各地区招生数量')
plt.xlabel('地区')
plt.ylabel('项目数量')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()
