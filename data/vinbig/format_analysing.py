import pandas as pd
import json

# 讀取 CSV
df = pd.read_csv('annotations.csv')
print("Annotations 範例:")
print(df.head())

# 讀取 JSON
with open('dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print("\nDataset JSON 範例:")
# 如果是 list 就印前兩筆，如果是 dict 就印 key
if isinstance(data, list):
    print(data[:2])
else:
    print(list(data.keys())[:5])