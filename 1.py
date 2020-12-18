from kivy.app import App
from kivy.lang import Builder

KV = """
Button:
    text: "Button"
    size_hint: None, None
    size: 1000, 50
    pos_hint: {"center_y": .7, "center_x": .5}
"""
KV1 = """
Button:
    text: "Button"
    size_hint: None, None
    size: 1000, 50
    pos_hint: {"center_y": .4, "center_x": .5}
"""


class MyApp(App):
    def build(self):
        return Builder.load_string(KV)

        return MyLayout()
class MyApp1(App):
    def build(self):
        return Builder.load_string(KV1)
        return MyLayout1()
if __name__ == '__main__':
    MyApp().run()
    MyApp1().run()