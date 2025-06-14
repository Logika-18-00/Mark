import pandas as pd
import matplotlib.pyplot as plt

# Завантаження даних
df = pd.read_csv('IMDB-Movie-Data.csv')

# Очищення даних
df_cleaned = df.dropna()
df_cleaned.to_csv('IMDB-Movie-Data-Cleaned.csv', index=False)
data = pd.read_csv('IMDB-Movie-Data-Cleaned.csv')

top_movies = data.sort_values(by='Rating', ascending=False).head(10)

print("\nТоп-10 фільмів за рейтингом користувачів:")
print(top_movies[['Title', 'Rating', 'Metascore']])