import pandas as pd

#Create Series from list
data = [20, 30, 40, 50, 10]
index = ['a', 'b', 'c', 'd', 'e']
series = pd.Series(data, index=index)
# print(series)


#data = {'a': 10, 'b': 20, 'c': 30, 'd': 40, 'e': 50}
#series_from_dict = pd.Series(data)
#print(series_from_dict.to_string())  #withopu dtype

data = {'a': 10, 'b': 20, 'c': 30, 'd': 40, 'e': 50}
series_from_dict = pd.Series(data)

#print(series_from_dict['b'])  # 20
#print(series_from_dict[2])  # 30

multiplied_series = series * 2
#print(multiplied_series) #a     40 and so on....

data = {'a': 10, 'b': 20, 'c': 30, 'd': 40, 'e': 50}
series = pd.Series(data)
another_series = pd.Series([5, 15, 25, 35, 45], index=['a', 'b', 'c', 'd', 'e'])
sum_series = series + another_series    #sum 2 series
#print(sum_series)


index = ['a', 'b', 'c', 'd', 'e']

# Создание Series с отсутствующими значениями
data_with_nan = [10, 20, None, 40, 50]
series_with_nan = pd.Series(data_with_nan, index=index)
print("Series с отсутствующими значениями:")
print(series_with_nan)

# Заполнение отсутствующих значений
filled_series = series_with_nan.fillna(0)
print("\nSeries с заполненными отсутствующими значениями:")
print(filled_series)

# Удаление отсутствующих значений
dropped_series = series_with_nan.dropna()
print("\nSeries без отсутствующих значений:")
print(dropped_series)