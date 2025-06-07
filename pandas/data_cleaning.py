import pandas as pd
df = pd.read_csv('GooglePlayStore_wild.csv')
# Виведи інформацію про всі DataFrame, щоб дізнатися, які стовпці потребують очищення
print(df.info())

# Скільки в датасеті додатків, у яких не вказано (NaN) рейтинг (Rating)?
print(len(df[pd.isnull(df["Rating"])]))
# Заміни порожнє значення ('NaN') рейтингу ('Rating') для таких програм на -1.
df["Rating"].fillna(-1, inplace = True)
# Визнач, яке ще значення розміру ('Size') зберігається в датасеті крім Кілобайтів та Мегабайтів, заміни його на -1.
print(df["Size"].value_counts())
# Перетвори розміри додатків ('Size') у числовий формат (float). Розмір усіх програм повинен вимірюватися в Мегабайтах.

# Чому дорівнює максимальний розмір ('Size') додатків з категорії ('Category') 'TOOLS'?
def set_size(size):
    if size[-1] == "M":
        return float(size[:-1])
    elif size[-1] == "M":
        return float(size[:-1]) / 1024
    return -1
df["Size"] = df["Size"].apply(set_size)

# Бонусні завдання
# Заміни тип даних на цілий (int) для кількості установок ('Installs').
# У записі кількості установок ('Installs') знак "+" необхідно ігнорувати.
# Тобто, якщо в датасеті кількість установок дорівнює 1,000,000+, необхідно змінити значення на 1000000
print(df[df["Category"] == "TOOLS"]["Size"].max())
# Згрупуй дані за категорією ('Category') та цільовою аудиторією ('Content Rating') будь-яким зручним для тебе способом,
# Порахуй середню кількість установок ('Installs') у кожній групі. Результат округлили до десятих.
# В отриманій таблиці знайди клітинку з найбільшим значенням.
# До якої вікової групи та типу додатків відносяться дані з цієї клітинки?
def set_installs(installs):
    if installs == 0:
        return 0
    return int(installs[:-1],replace(",", ""))
df["Installs"] = df["Installs"].apply(set_installs) 

print(round(df.pivot_table(index = "Content Rating", columns= "Type", values = "Installs", aggfunc = "mean")), 1)
print(df[pd.isnull(df["Type"])])

df["Type"].fillna("Free", inplace = "True")
# У якої програми не вказаний тип ('Type')? Який тип там потрібно записати залежно від ціни?
print(df.info())
# Виведи інформацію про все DataFrame, щоб переконатися, що очищення пройшло успішно