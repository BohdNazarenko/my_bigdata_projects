import pandas as pd

# Создание первого объекта Series
points_per_game = pd.Series(
    [27.3, 26.0, 21.5, 16.3],
    index=[201939, 201142, 202691, 202326],
    name='pts_per_game'
)

# Создание второго объекта Series
rebounds_per_game = pd.Series(
    [5.3, 6.4, 3.8, 8.2],
    index=[201939, 201142, 202691, 202326],
    name='reb_per_game'
)

# Объединение двух Series в DataFrame
df = pd.DataFrame({
    'player_id': points_per_game.index,
    'pts_per_game': points_per_game.values,
    'reb_per_game': rebounds_per_game.values
})

print(df)