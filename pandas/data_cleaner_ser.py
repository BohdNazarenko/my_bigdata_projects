import pandas as pd
import numpy as np

# Создание Series с пропущенными значениями
s = pd.Series([1, 2, np.nan, 4, np.nan, 6])

# 1. Удаление пропущенных значений
s_dropped = s.dropna()
print("Удаление пропущенных значений:")
print(s_dropped)

# 2. Заполнение пропущенных значений определенным значением
s_filled = s.fillna(0)
print("\nЗаполнение пропущенных значений нулями:")
print(s_filled)

# 3. Заполнение пропущенных значений средним значением серии
s_filled_mean = s.fillna(s.mean())
print("\nЗаполнение пропущенных значений средним значением:")
print(s_filled_mean)


# Создание Series с дубликатами
s = pd.Series([1, 2, 2, 3, 4, 4, 4, 5])

# 1. Определение дубликатов
duplicates = s.duplicated()
print("\nОпределение дубликатов в Series:")
print(duplicates)

# 2. Удаление дубликатов
s_no_duplicates = s.drop_duplicates()
print("\nУдаление дубликатов из Series:")
print(s_no_duplicates)




data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100]
s = pd.Series(data)

# Вычисление первого и третьего квартилей
Q1 = s.quantile(0.25)  # Первый квартиль (25-й процентиль)
Q3 = s.quantile(0.75)  # Третий квартиль (75-й процентиль)

# Вычисление IQR
IQR = Q3 - Q1

# Определение границ выбросов
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

print(f"IQR: {IQR}")
print(f"Нижняя граница выбросов: {lower_bound}")
print(f"Верхняя граница выбросов: {upper_bound}")

# Выявление выбросов
outliers = s[(s < lower_bound) | (s > upper_bound)]
print(f"Выбросы в данных: {outliers.tolist()}")