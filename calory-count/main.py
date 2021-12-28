import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

from kivy.lang import Builder
from kivymd.app import MDApp

class CaloryApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_file("main.kv")

if __name__ ==  '__main__':
    CaloryApp().run()
