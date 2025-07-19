import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Завантажуємо та готуємо дані
data = pd.read_csv('train.csv').fillna({
    'has_photo': 0, 'has_mobile': 0, 'followers_count': 0, 'relation': 0
})

# Топ-10 мов
top_languages = pd.Series(
    [lang.strip() for langs in data['langs'].dropna() for lang in langs.split(';')]
).value_counts().head(10).index

# розділяємо мови на стовпці
for lang in top_languages:
    data[f'lang_{lang}'] = data['langs'].str.contains(lang, na=False).astype(int)

# x= ознаки за якими модель буде визначати статтю. y = ціль(стать)
X = pd.get_dummies(data[['has_photo', 'has_mobile', 'followers_count', 'relation'] + 
                       [f'lang_{lang}' for lang in top_languages]], 
                  columns=['relation'])

y = data['sex']

# Тренування моделі
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Оцінка
y_pred = model.predict(X_test)
print(f"Точність: {accuracy_score(y_test, y_pred):.2f}\n")
print(classification_report(y_test, y_pred))

# Топ-10 ознак
feature_importances = pd.DataFrame({
    'Ознака': X.columns,
    'Важливість': model.feature_importances_
}).sort_values('Важливість', ascending=False).head(10)

print("\nТоп-10 найважливіших ознак:")
print(feature_importances.to_string(index=False))