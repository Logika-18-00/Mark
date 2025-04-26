import json

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen


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
    def __init__(self,**kw):
        super().__init__(**kw)

    def on_shop_screen(self, *args):
        self.manager.current = "shop"

    def on_enter(self, *args):
        self.ids.score_lbl.text = "рахунок: "+ str(player["score"])

    def click(self):
        self.ids.click.size_hint = (1, 1)
        read_data()
        player["score"] += player["power"]
        self.ids.score_lbl.text = "рахунок: "+ str(player["score"])
        save_data()
    def unclick(self):
        self.ids.click.size_hint = (0.5, 0.5)

class SecondScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)

class MenuScreen(Screen):
    def __init__(self,**kw):
        super().__init__(**kw)

    def on_main_screen(self, *args):
        self.manager.current = "main"

    def on_second_screen(self, *args):
        self.manager.current = "second"



class ShopScreen(Screen):
    def __init__(self,**kw):
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



app = ClickerApp()
app.run()

