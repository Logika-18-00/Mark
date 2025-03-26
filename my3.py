from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
def test(instanss):
        print("Okis Mark")

class MyApp(App):
    
    def build(self):
        txt = Label(text = "Моя перша програма")
        btn = Button(text= "Це кнопка")
        btn.bind(on_press = test)
        layout = BoxLayout()
        layout.add_widget(txt)
        layout.add_widget(btn)
        return layout


app = MyApp()
app.run()