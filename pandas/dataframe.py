import pandas as pd

data = {
    'Name': ['Alice', 'Bob', 'Cathy', 'David'],
    'Age': [25, 30, 29, 35],
    'City': ['New York', 'Los Angeles', 'Chicago', 'Houston']
}

df = pd.DataFrame(data)
#print(df)


data = [
    ['Alice', 25, 'New York'],
    ['Bob', 30, 'Los Angeles'],
    ['Cathy', 29, 'Chicago'],
    ['David', 35, 'Houston']
]

df = pd.DataFrame(data, columns=['Name', 'Age', 'City'])
#print(df)


df = pd.read_csv('data.csv')

#
# print(df.head(2))
# print(df.tail(2))
# #print(df.info())
# print('\n',df['player_id'])


df1 = pd.DataFrame({
    'A': ['A0', 'A1', 'A2', 'A3'],
    'B': ['B0', 'B1', 'B2', 'B3']
}, index=[0, 1, 2, 3])

df2 = pd.DataFrame({
    'A': ['A4', 'A5', 'A6', 'A7'],
    'B': ['B4', 'B5', 'B6', 'B7']
}, index=[4, 5, 6, 7])

# Конкатенация двух DataFrame по строкам (axis=0)
result_concat = pd.concat([df1, df2], axis=0)
print("Конкатенация по строкам:\n", result_concat)

# Конкатенация двух DataFrame по столбцам (axis=1)
result_concat_cols = pd.concat([df1, df2], axis=1)
print("\nКонкатенация по столбцам:\n", result_concat_cols)



import pandas as pd
df1 = pd.DataFrame({
    'Key': ['K0', 'K1', 'K2', 'K3'],
    'A': ['A0', 'A1', 'A2', 'A3'],
    'B': ['B0', 'B1', 'B2', 'B3']
})

df2 = pd.DataFrame({
    'Key': ['K0', 'K1', 'K2', 'K4'],
    'C': ['C0', 'C1', 'C2', 'C4'],
    'D': ['D0', 'D1', 'D2', 'D4']
})

# Слияние двух DataFrame по общему столбцу 'Key'
result_merge = pd.merge(df1, df2, on='Key', how='inner')
print("\nСлияние по общему столбцу 'Key' (inner join):\n", result_merge)

# Слияние двух DataFrame с внешним объединением (outer join)
result_merge_outer = pd.merge(df1, df2, on='Key', how='outer')
print("\nСлияние с внешним объединением (outer join):\n", result_merge_outer)