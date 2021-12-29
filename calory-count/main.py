import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from datetime import datetime as dt

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivymd.uix.label import Label

from meal_db import Meal, MealDB

class CaloryApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        return Builder.load_file("main.kv")
    def on_add_meal_button_pressed(self):
        """ When  the Submit meal button is pressed:
                1. asserts the inputs are good.
                2. Adds a new meal.
                3. Clears the inputs.
        """
        if not self.is_meal_input_ok():
            return
        proteins, fats, carbs = self._protiens_fats_carbs()
        meal = Meal( name = self.root.ids.meal_name_input.text,
                     date = dt.now().isoformat(),
                     grams = float(self.root.ids.grams_input.text),
                     proteins = proteins,
                     fats = fats,
                     carbs = carbs,
                     cals = (proteins + carbs)*4 + fats*9
                    )
        with MealDB() as mdb:
            mdb.add_meal(meal)
        self.on_clear_meal_button_pressed()
        self.root.ids.add_meal_label.text = "New meal Added"

    def _protiens_fats_carbs(self) -> tuple[int]:
        """Helper method for getting the 3 sliders values"""
        sliders = [self.root.ids.protein_slider, self.root.ids.fats_slider, self.root.ids.carbs_slider]
        return tuple(int(x.value) for x in sliders if x.value)
    def is_meal_input_ok(self) -> bool:
        """ Making sure that the inputs are good for adding to DB """
        errors = []  # Errors will be added here
        if not sum(self._protiens_fats_carbs()) == 100:
            errors.append('Proteins fats and Crabs do not add up to 100.')
        if not self.root.ids.grams_input.text:
           errors.append('Grams was not specified')
        elif not all(x.isalnum() for x in self.root.ids.grams_input.text):
            errors.append('Grams must be a number.')
        if errors:
            Popup(title="Can't Add Meal",
                  content=Label(text='\n'.join(errors)),
                  size_hint=(0.5, 0.3)).open()
            return False
        return True
    def on_clear_meal_button_pressed(self):
        self.root.ids.add_meal_label.text = ""
        self.root.ids.protein_slider.value = 0
        self.root.ids.fats_slider.value = 0
        self.root.ids.carbs_slider.value = 0
    def on_meal_slide(self, slider, val):
         """Event that occurs on sliders value changed in add meal screen"""
         left_over = int(100 - sum(self._protiens_fats_carbs()))
         if left_over < 0:
             slider.value = val - 1

    def on_daily_screen_pressed(self, *args):
        with MealDB() as mdb:
            cals = sum(meal.cals for meal in mdb.get_all_meals())
            self.root.ids.total_cals_label.text = str(cals)

if __name__ ==  '__main__':
    CaloryApp().run()

