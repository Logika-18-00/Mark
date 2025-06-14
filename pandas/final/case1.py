import pandas as pd
import matplotlib.pyplot as plt

# Завантаження даних
df = pd.read_csv('IMDB-Movie-Data.csv')

# Очищення даних
df_cleaned = df.dropna()
df_cleaned.to_csv('IMDB-Movie-Data-Cleaned.csv', index=False)
data = pd.read_csv('IMDB-Movie-Data-Cleaned.csv')

# Додавання нового стовпця "Actor-Director"
data['Actor-Director'] = data['Actors'] + ' - ' + data['Director']

# Групування за комбінацією актор-режисер та обчислення середнього рейтингу на Metascore
actor_director_rating = data.groupby('Actor-Director')['Metascore'].mean().reset_index()
actor_director_rating = actor_director_rating.sort_values(by='Metascore', ascending=False)

print("\nТоп-10 комбінацій 'актор-режисер' за середнім рейтингом на Metacritic:")
print(actor_director_rating.head(10))
# Побудова стовпчикового графіка
plt.figure(figsize=(12, 8))
plt.barh(actor_director_rating['Actor-Director'].head(10), actor_director_rating['Metascore'].head(10), color='skyblue')
plt.title('Топ-10 комбінацій актор-режисер за середнім Metascore')
plt.xlabel('Середній Metascore')
plt.ylabel('Актор - Режисер')
plt.grid(True)
plt.gca().invert_yaxis()  # Інвертуємо вісь Y для кращого вигляду
plt.show()
