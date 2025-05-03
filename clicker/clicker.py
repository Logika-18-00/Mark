import json
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout

player = {
    "score": 0,
    "power": 1
}

def read_data():
    global player
    try:
        with open("play.json", "r", encoding="utf-8") as file:
            player = json.load(file)
    except:
        print("невдача((((")

read_data()

def save_data():
    global player
    try:
        with open("play.json", "w", encoding="utf-8") as file:
            json.dump(player, file, indent=4, ensure_ascii=True)
    except:
        print("невдача((((")

class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_shop_screen(self, *args):
        self.manager.current = "shop"

    def click(self):
        read_data()
        player["score"] += player["power"]
        self.ids.score_lbl.text = "рахунок: " + str(player["score"])
        self.ids.click.size_hint = (1, 1)
        save_data()
        
        # Вибиваємо силу кліку в випадкових координатах
        self.show_power()

    def unclick(self):
        self.ids.click.size_hint = (0.5, 0.5)
        self.ids.click.source = "click.png"

    def show_power(self):
        # Створюємо новий Label для відображення сили кліку
        power_label = Label(
            text=f"+ {player['power']}",
            size_hint=(None, None),
            size=(200, 50)
        )
        
        # Генеруємо випадкові координати
        x = random.uniform(0, self.width - 200)
        y = random.uniform(0, self.height - 50)
        
        # Встановлюємо позицію
        power_label.pos = (x, y)
        
        # Додаємо Label до екрану
        self.add_widget(power_label)

        # Запускаємо таймер для видалення Label через 2 секунди
        Clock.schedule_once(lambda dt: self.remove_widget(power_label), 2)

class SecondScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_main_screen(self, *args):
        self.manager.current = "main"

    def on_second_screen(self, *args):
        self.manager.current = "second"

class ShopScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def on_enter(self, *args):
        self.ids.money.text = "Рахунок: " + str(player["score"])

    def buy(self, price, power):
        read_data()
        if price <= player["score"]:
            player["score"] -= price
            player["power"] += power
            self.ids.money.text = "Рахунок: " + str(player["score"])
            save_data()

    def on_main_screen(self, *args):
        self.manager.current = "main"

class ClickerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SecondScreen(name='second'))
        sm.add_widget(ShopScreen(name='shop'))
        return sm

if __name__ == '__main__':
    app = ClickerApp()
    app.run()
