from kivy.app import App
from kivy.uix.label import Label
from kivy.core.window import Window
Window.clearcolor = (0.12, 0.12, 0.12, 1)   # opaque!

class T(App):
    def build(self):
        return Label(text="Hello Kivy", font_size="40sp")
T().run()