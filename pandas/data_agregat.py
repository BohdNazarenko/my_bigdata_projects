import pandas as pd

# Пример DataFrame
df = pd.DataFrame({
    'Category': ['A', 'B', 'A', 'B', 'C', 'A'],
    'Values': [10, 20, 15, 25, 10, 30]
})

# Группировка по столбцу 'Category' и вычисление суммы значений в каждой группе
grouped_df = df.groupby('Category').sum()
print("Группировка DataFrame по столбцу 'Category' с суммированием:")
print(grouped_df)



# Группировка по столбцу 'Category' и вычисление суммы значений в каждой группе
grouped_df = df.groupby('Category', as_index=False).sum()
print("Группировка DataFrame по столбцу 'Category' с суммированием:")
print(grouped_df)


# Пример Series
s = pd.Series([10, 20, 15, 25, 10, 30], index=['A', 'B', 'A', 'B', 'C', 'A'])

# Группировка по индексу и вычисление суммы значений в каждой группе
grouped_s = s.groupby(level=0).sum()
print("\nГруппировка Series по индексу с суммированием:")
print(grouped_s)


# Пример DataFrame
df = pd.DataFrame({
    'Category': ['A', 'B', 'A', 'B', 'C', 'A'],
    'Values': [10, 20, 15, 25, 10, 30]
})

# Агрегация данных: вычисление суммы и среднего значений в каждой группе
agg_df = df.groupby('Category').agg({'Values': ['sum', 'mean']})
print("\nАгрегация DataFrame по столбцу 'Category' с суммой и средним:")
print(agg_df)



# Пример Series
s = pd.Series([10, 20, 15, 25, 10, 30], index=['A', 'B', 'A', 'B', 'C', 'A'])

# Агрегация данных: вычисление суммы и среднего значений в каждой группе
agg_s = s.groupby(level=0).agg(['sum', 'mean'])
print("\nАгрегация Series по индексу с суммой и средним:")
print(agg_s)

#moda
df = pd.DataFrame({
    'Category': ['A', 'B', 'A', 'B', 'C', 'A'],
    'Values': [10, 20, 15, 25, 10, 30]
})

grouped_mode = df.groupby('Category')['Values'].apply(lambda x: x.mode())
print("\nMode (мода) для каждой категории:")
print(grouped_mode)


grouped_quantile = df.groupby('Category')['Values'].quantile(0.5)
print("\nМедиана (50-й процентиль) для каждой категории:")
print(grouped_quantile)




# Создание двух Series для примера
s1 = pd.Series([1, 2, 3], index=['A', 'B', 'C'])
s2 = pd.Series([4, 5, 6], index=['A', 'B', 'D'])

# Объединение Series по строкам (по умолчанию axis=0)
concat_s = pd.concat([s1, s2])
print("\nОбъединение Series по строкам:")
print(concat_s)

# Объединение Series по столбцам (axis=1)
concat_s_axis1 = pd.concat([s1, s2], axis=1)
print("\nОбъединение Series по столбцам:")
print(concat_s_axis1)


# Создание двух Series для примера
s1 = pd.Series([1, 2, 3], index=['A', 'B', 'C'])
s2 = pd.Series([4, 5, 6], index=['A', 'B', 'D'])

# Преобразование Series в DataFrame
df1 = s1.reset_index()
df1.columns = ['Key', 'Value1']

df2 = s2.reset_index()
df2.columns = ['Key', 'Value2']

# Объединение DataFrame с использованием merge
merged_series_df = pd.merge(df1, df2, on='Key', how='outer')
print("\nОбъединение Series после преобразования в DataFrame:")
print(merged_series_df)


# Группировка DataFrame по столбцу 'Category' с суммированием:
#           Values
# Category
# A             55
# B             45
# C             10
# Группировка DataFrame по столбцу 'Category' с суммированием:
#   Category  Values
# 0        A      55
# 1        B      45
# 2        C      10
#
# Группировка Series по индексу с суммированием:
# A    55
# B    45
# C    10
# dtype: int64
#
# Агрегация DataFrame по столбцу 'Category' с суммой и средним:
#          Values
#             sum       mean
# Category
# A            55  18.333333
# B            45  22.500000
# C            10  10.000000
#
# Агрегация Series по индексу с суммой и средним:
#    sum       mean
# A   55  18.333333
# B   45  22.500000
# C   10  10.000000
#
# Mode (мода) для каждой категории:
# Category
# A         0    10
#           1    15
#           2    30
# B         0    20
#           1    25
# C         0    10
# Name: Values, dtype: int64
#
# Медиана (50-й процентиль) для каждой категории:
# Category
# A    15.0
# B    22.5
# C    10.0
# Name: Values, dtype: float64
#
# Объединение Series по строкам:
# A    1
# B    2
# C    3
# A    4
# B    5
# D    6
# dtype: int64
#
# Объединение Series по столбцам:
#      0    1
# A  1.0  4.0
# B  2.0  5.0
# C  3.0  NaN
# D  NaN  6.0
#
# Объединение Series после преобразования в DataFrame:
#   Key  Value1  Value2
# 0   A     1.0     4.0
# 1   B     2.0     5.0
# 2   C     3.0     NaN
# 3   D     NaN     6.0
