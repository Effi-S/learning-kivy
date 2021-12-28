import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class MyGridLayout(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # set columns
        self.cols = 1

        # Creating second layout
        self.top_grid = GridLayout()
        self.top_grid.cols = 2

        # Adding widget1
        self.top_grid.add_widget(Label(text="Name: "))
        self.name = TextInput(multiline=False)
        self.top_grid.add_widget(self.name)

        # Adding widget2
        self.top_grid.add_widget(Label(text="Quest: "))
        self.quest = TextInput(multiline=False)
        self.top_grid.add_widget(self.quest)

        # Adding widget3
        self.top_grid.add_widget(Label(text="Favourite Color?: "))
        self.color = TextInput(multiline=False)
        self.top_grid.add_widget(self.color)

        # Add top_grid
        self.add_widget(self.top_grid)

        # Add submit Button
        self.submit = Button(text='Submit', font_size=32, size_hint_y=None, height=100)

	# -- Bind Button
        self.submit.bind(on_press=self.on_submit_pressed)
        # -- make it span 2 columns
        self.add_widget(self.submit)

    def on_submit_pressed(self, event):
        name = self.name.text
        quest = self.quest.text
        color =  self.color.text
        print(name, quest, color)


class MyApp(App):
    def build(self):
        return MyGridLayout()

if __name__ == '__main__':
    MyApp().run()

