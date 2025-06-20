import pandas as pd
import matplotlib.pyplot as plt

# Завантаження та очищення даних
df = pd.read_csv('IMDB-Movie-Data.csv')
df_cleaned = df.dropna()
data = df_cleaned.copy()

# Розрахунок середніх рейтингів жанрів
genre_dummies = data['Genre'].str.get_dummies(sep=',')
genre_rating = genre_dummies.mul(data['Rating'], axis=0).sum().div(genre_dummies.sum()).reset_index()
genre_rating.columns = ['Genre', 'Average Rating']
genre_rating = genre_rating.sort_values(by='Average Rating', ascending=False)

# Вибір топ-10 жанрів
top_genres = genre_rating.head(10)

# Створення гістограми
plt.figure(figsize=(12, 6))
bars = plt.bar(top_genres['Genre'], top_genres['Average Rating'], color='skyblue')

# Додавання значень на стовпці
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}',
             ha='center', va='bottom', fontsize=10)

# Налаштування вигляду графіка
plt.title('Топ-10 жанрів за середнім рейтингом IMDB', fontsize=14, pad=20)
plt.xlabel('Жанр', fontsize=12)
plt.ylabel('Середній рейтинг', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.ylim(top_genres['Average Rating'].min() - 0.2, top_genres['Average Rating'].max() + 0.1)
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()