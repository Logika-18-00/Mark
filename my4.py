from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen

class FirstScr(Screen):
    def __init__(self, name = "first"):
        super().__init__(name=name)
        btn = Button(text= "Це кнопка")
        btn.on_press = self.next
        self.add_widget(btn)
    def next(self):
        self.manager.transition.direction = "left"
        self.manager.current = "second"

class SecondScr(Screen):
    def __init__(self, name = "first"):
        super().__init__(name=name)
        btn = Button(text= "Назад")
        btn.on_press = self.next
        self.add_widget(btn)


    def next(self):
        self.manager.transition.direction = 'right'
        self.manager.current = 'first'

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(FirstScr(name='first'))
        sm.add_widget(SecondScr(name='second'))
        sm.current = "second"
        return sm
    

app = MyApp()
app.run()