import pandas as pd
import matplotlib.pyplot as plt

# Завантаження даних
df = pd.read_csv('IMDB-Movie-Data.csv')

# Очищення даних
df_cleaned = df.dropna()

# Отримуємо топ-10 унікальних фільмів за рейтингом
top_movies = df_cleaned.sort_values(by='Rating', ascending=False).drop_duplicates(subset=['Title']).head(10)

# Перевірка кількості фільмів
if len(top_movies) < 3:  # Мінімум 3 фільми для кругової діаграми
    print("Попередження: Замало даних для побудови діаграми. Знайдено фільмів:", len(top_movies))
    print("Список фільмів:")
    print(top_movies[['Title', 'Rating']])
else:
    # Створення кругової діаграми
    plt.figure(figsize=(12, 12))
    colors = plt.cm.tab20c.colors

    # Визначаємо функцію для відображення значень
    def format_func(pct, allvals):
        absolute = pct/100.*sum(allvals)
        return f"{absolute:.1f}"

    # Малюємо діаграму (без спроби розпакування)
    pie = plt.pie(top_movies['Rating'],
                 labels=top_movies['Title'],
                 autopct=lambda pct: format_func(pct, top_movies['Rating']),
                 startangle=90,
                 colors=colors,
                 wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
                 textprops={'fontsize': 10})

    plt.title(f'Топ-{len(top_movies)} унікальних фільмів за рейтингом IMDB', pad=20, fontsize=14)
    plt.axis('equal')
print("\nТоп-10 фільмів за рейтингом користувачів:")
print(top_movies[['Title', 'Rating', 'Metascore']])

plt.tight_layout()
plt.show()
