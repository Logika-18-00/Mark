from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout


class MyApp(App):
    def build(self):
        txt = Label(text = "Моя перша програма")
        btn = Button(text= "Це кнопка")
        layout = BoxLayout()
        layout.add_widget(txt)
        layout.add_widget(btn)
        return layout


app = MyApp()
app.run()