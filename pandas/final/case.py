import pandas as pd

# Крок 1: Завантаження даних
df = pd.read_csv('IMDB-Movie-Data.csv')

# Крок 2: Очищення даних - видалення рядків з будь-якими пропущеними значеннями
df_cleaned = df.dropna()

# Крок 3: Збереження очищеного набору даних
df_cleaned.to_csv('IMDB-Movie-Data-Cleaned.csv', index=False)

# Крок 4: Виведення інформації про оригінальний набір даних
print("Інформація про оригінальний набір даних:")
print(df.info())

# Крок 5: Завантаження очищеного набору даних для аналізу
data = pd.read_csv('IMDB-Movie-Data-Cleaned.csv')

# Крок 6: Створення комбінованого стовпця "актор-режисер"
data['Actor-Director'] = data['Actors'] + ' - ' + data['Director']

# Крок 7: Групування за комбінацією актор-режисер та обчислення середнього рейтингу на Metascore
actor_director_rating = data.groupby('Actor-Director')['Metascore'].mean().reset_index()
actor_director_rating = actor_director_rating.sort_values(by='Metascore', ascending=False)

# Крок 8: Визначення топ-10 фільмів за рейтингом користувачів
top_movies = data.sort_values(by='Rating', ascending=False).head(10)

# Крок 9: Аналіз жанрів - обчислення середнього рейтингу за жанрами
# Розділення жанрів на думі-перемінні
genre_dummies = data['Genre'].str.get_dummies(sep=',')
genre_rating = genre_dummies.mul(data['Rating'], axis=0).sum().div(genre_dummies.sum()).reset_index()
genre_rating.columns = ['Genre', 'Average Rating']
genre_rating = genre_rating.sort_values(by='Average Rating', ascending=False)

# Крок 10: Виведення результатів
print("\nТоп-10 фільмів за рейтингом користувачів:")
print(top_movies[['Title', 'Rating', 'Metascore']])

print("\nТоп-10 комбінацій 'актор-режисер' за середнім рейтингом на Metacritic:")
print(actor_director_rating.head(10))

print("\nТоп-10 жанрів за середнім рейтингом:")
print(genre_rating.head(10))
