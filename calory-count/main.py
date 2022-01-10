from __future__ import annotations
import os
from typing import Optional

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # for debugging with GPU (must be before imports)

from kivymd.uix.picker import MDDatePicker, MDThemePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu

from kivy.clock import Clock

from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable

from kivy.lang import Builder
from kivymd.app import MDApp

from DB.meal_entry_db import MealEntriesDB, MealEntry
from kivy.uix.popup import Popup
from kivymd.uix.textfield import MDTextField
from kivymd.uix.slider import MDSlider
from kivymd.uix.label import MDLabel
from datetime import datetime as dt

from utils import sort_by_similarity
from meal_add_dialog import MealAddDialog
from DB.meal_db import Meal, MealDB


class CaloriesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_meal_dialog = None
        self.meals_table = None
        self._drop_down = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        Clock.schedule_once(lambda x: self.on_my_meals_screen_pressed())  # loading table
        return Builder.load_file("kv_files/main.kv")

    def on_daily_screen_pressed(self, *args):
        with MealEntriesDB() as me_db:
            today = dt.now().date().isoformat()
            cals = sum(e.meal.cals for e in me_db.get_entries_between_dates(today, today))
            self.root.ids.total_cals_label.text = str(cals)

    def on_my_meals_screen_pressed(self, *args):
        with MealDB() as mdb:
            meals = mdb.get_all_meals()

        table_layout = self.root.ids.meals_screen.ids.my_meals_layout
        table_layout.clear_widgets()
        self.meals_table = MDDataTable(column_data=[(col, dp(30)) for col in Meal.columns()],
                                       row_data=[m.values for m in meals],
                                       check=True,
                                       use_pagination=True
                                       )
        if not meals:
            self.meals_table.title = 'No Meals Yet'
            toast('No Meals Yet')

        table_layout.add_widget(self.meals_table)

    def on_add_meal_pressed(self, *args):
        if not self.add_meal_dialog:
            self.add_meal_dialog = MealAddDialog(self.root_window)
            self.add_meal_dialog.bind(on_dismiss=self.on_my_meals_screen_pressed)
        self.add_meal_dialog.open()

    def on_trends_pressed(self, *args, _once=[]):  # Note: mutable default parameter is on purpose here
        """"""
        if not _once:
            # Setting the Date in trends
            today = dt.now().date().isoformat()
            start = self.root.ids.trends_screen.ids.trend_start_date_button
            end = self.root.ids.trends_screen.ids.trend_end_date_button
            start.text += f'\n{today}'
            end.text += f'\n{today}'
            _once.append(1)
        self.generate_trend()

    def on_name_entered_in_add_entry_screen(self, c: str, *args):
        text_field = self.root.ids.entry_add_screen.ids.meal_name_input
        target = text_field.text + c
        self._drop_down = MDDropdownMenu(
            caller=text_field,
            width_mult=4)

        def callback(txt: str) -> None:
            self.root.ids.entry_add_screen.ids.meal_name_input.text = txt
            with MealDB() as db:
                self.root.ids.entry_add_screen.ids.grams_input.text = str(db.get_meal_by_name(txt).portion)

        with MealDB() as mdb:
            names = sort_by_similarity(mdb.get_all_meal_names(), target)
            for name in names[:5]:
                self._drop_down.items.append({'viewclass': 'OneLineListItem',
                                              'text': name,
                                              'on_release': lambda txt=name: callback(txt)
                                              })

        self._drop_down.open()
        return c

    def on_submit_meal_entry(self, *args):

        name = self.root.ids.entry_add_screen.ids.meal_name_input.text
        portion = self.root.ids.entry_add_screen.ids.grams_input.text
        with MealDB() as mdb:
            names = mdb.get_all_meal_names()
        if name not in names:
            print('On submit meal entry', *args)

            # Get meal from dialog
            def add_nameless_submission(*a, **k) -> None:
                if not dialog.check_errors():
                    with MealEntriesDB() as entries:
                        entry = MealEntry(meal=dialog.last_submission)
                        entries.add_meal_entry(entry)
                        toast(f'Added Meal entry!\n({entry}')

            dialog = MealAddDialog(self.root_window, allow_nameless=True)
            dialog.meal_name.text, dialog.title = name, f'"{name}" not in Meals, Please add it below:'
            dialog.open()
            dialog.bind(on_dismiss=add_nameless_submission)
        else:
            with MealEntriesDB() as me_db:
                me = MealEntry(name=name, portion=float(portion or 0))
                me_db.add_meal_entry(me)
                toast(f'Added Meal entry!\n({me}')

    def on_delete_meals_pressed(self, *args):
        print('On Delete Meals Pressed')
        names = [x[0] for x in self.meals_table.get_row_checks()]

        def remove(*a, **k):
            with MealDB() as mdb:
                mdb.remove(names)
                dialog.dismiss()
                self.on_my_meals_screen_pressed()
                toast(f'Removed {len(names)} Meal/s')

        dialog = MDDialog(
            text=f"Are you sure you want to delete {len(names)} rows?",
            buttons=[MDFlatButton(text="CANCEL",
                                  theme_text_color="Custom",
                                  text_color=self.theme_cls.primary_color,
                                  on_press=lambda *a, **k: dialog.dismiss()),
                     MDFlatButton(
                         text="DELETE",
                         theme_text_color="Custom",
                         text_color=self.theme_cls.primary_color,
                         on_press=remove),
                     ],
        )
        dialog.open()

    @staticmethod
    def show_date_picker(button, *args, **kwargs):
        print('In show_date_picker:', *args, kwargs)

        def got_date(_, date, *a, **k):
            button.text = button.text.splitlines()[0] + '\n' + date.isoformat()

        picker = MDDatePicker()
        picker.bind(on_save=got_date)
        picker.open()

    def generate_trend(self, *args, **kwargs):
        print("in Generate Trends:", *args, kwargs)
        trend_chart_layout = self.root.ids.trends_screen.ids.trend_chart_layout
        start_date = self.root.ids.trends_screen.ids.trend_start_date_button.text.splitlines()[-1]
        end_date = self.root.ids.trends_screen.ids.trend_end_date_button.text.splitlines()[-1]
        trend_chart_layout.clear_widgets()
        with MealEntriesDB() as me_db:
            entries = me_db.get_entries_between_dates(str(start_date), str(end_date))
        print(entries)

    @staticmethod
    def show_theme_picker(*args, **kwargs):
        theme_dialog = MDThemePicker()
        theme_dialog.open()


if __name__ == '__main__':
    CaloriesApp().run()
