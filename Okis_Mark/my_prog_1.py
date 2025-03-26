from kivy.app import App
from kivy.uix.button import Button

class MyApp(App):
    def build(self):
        btn = Button(text= "Це кнопка")
        return btn

app = MyApp()
app.run()