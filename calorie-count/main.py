from __future__ import annotations

import configparser
import os

os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'  # Remove when not on windows (debug w/ GPU)

from kivy.uix.screenmanager import ScreenManager

from dialogs.meal_search import MealSearchScreen

import re
from daily_screen import init_daily_screen
from plotting import plot_pie_chart, plot_graph
from kivymd.uix.picker import MDDatePicker, MDThemePicker
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.menu import MDDropdownMenu

from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable

from kivy.lang import Builder
from kivymd.app import MDApp

from DB.meal_entry_db import MealEntriesDB, MealEntry

from datetime import datetime as dt
from datetime import timedelta, date

from utils import sort_by_similarity
from dialogs.meal_add_dialog import MealAddDialog
from DB.meal_db import Meal, MealDB

CONFIG, THEME = 'DB/config.ini', 'THEME'


class CaloriesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_meal_dialog = None
        self.meals_table = None
        self._drop_down = None

    def build(self):
        parser = configparser.ConfigParser()
        parser.read(CONFIG)
        self.theme_cls.theme_style = parser.get(THEME, 'theme_style', fallback="Dark")
        self.theme_cls.accent_palette = parser.get(THEME, 'accent_palette', fallback="Teal")
        self.theme_cls.primary_palette = parser.get(THEME, 'primary_palette', fallback="BlueGray")
        Clock.schedule_once(self._post_build_)

        # setting entry date to today
        def _set_entry_date():
            self.root.ids.entry_add_screen.ids.date_input.text = f'Date:\n{dt.now().date().isoformat()}'

        Clock.schedule_once(lambda *_: _set_entry_date())

        from kivy.core.window import Window
        Window.size = (500, 700)
        return Builder.load_file("kv_files/main.kv")

    def _post_build_(self, *a, **k):
        self.on_my_meals_screen_pressed()  # loading table
        self._switch_tab()  # setting default tab
        self.meal_search_screen = MealSearchScreen(self)
        self.root.add_widget(self.meal_search_screen)

    def _switch_tab(self, name: str = 'add_entry'):
        """Helper for switching the current tab."""
        self.root.ids.bottom_navigation.switch_tab(name)

    def on_choose_entry_date_pressed(self):
        """Set a custom date for the entry"""
        self.show_date_picker(button=self.root.ids.entry_add_screen.ids.date_input,
                              is_limited=False)

    def on_daily_screen_pressed(self, *args):
        """Init Daily screen"""
        init_daily_screen(self)

    def _find_day_in_daily_screen(self) -> date:
        """Get a date object parsed from the label displayed in Daily screen"""
        text = self.root.ids.total_cals_header_label.text
        if 'today' in text.lower():
            return dt.now().date()
        elif 'yesterday' in text.lower():
            return (dt.now() - timedelta(days=1)).date()
        for day in re.findall(r'\d+-\d+-\d+', text):
            return dt.fromisoformat(day).date()
        toast('Error Getting day')

    def on_prev_daily_pressed(self, *args):
        """Previous day in Daily tab"""
        day = self._find_day_in_daily_screen() - timedelta(days=1)
        init_daily_screen(self, day)

    def on_next_daily_pressed(self, *args):
        """Next day in Daily tab"""
        day = self._find_day_in_daily_screen() + timedelta(days=1)
        if day > dt.now().date():
            return
        init_daily_screen(self, day)

    def on_my_meals_screen_pressed(self, *args):
        with MealDB() as mdb:
            meals = mdb.get_all_meals()

        table_layout = self.root.ids.meals_screen.ids.my_meals_layout
        table_layout.clear_widgets()
        self.meals_table = MDDataTable(column_data=[(col, dp(30)) for col in Meal.columns()],
                                       row_data=[[f'[font=Arial]{x}[/font]' for x in m.values]
                                                 for m in meals],
                                       check=True,
                                       use_pagination=True
                                       )
        if not meals:
            self.meals_table.title = 'No Meals Yet'
            toast('No Meals Yet')

        table_layout.add_widget(self.meals_table)

    def on_add_meal_pressed(self, *args):
        if not self.add_meal_dialog:
            self.add_meal_dialog = MealAddDialog(self)
        self.add_meal_dialog.open()

    def on_trends_pressed(self, *args, _once=[]):  # Note: mutable default parameter is on purpose here
        """Event when entering the "Trends" screen """
        if not _once:
            # Setting the Dates in trends between today and 7 days ago
            today = dt.now().date().isoformat()
            a_week_ago = dt.now().date() - timedelta(days=7)
            start = self.root.ids.trends_screen.ids.trend_start_date_button
            end = self.root.ids.trends_screen.ids.trend_end_date_button
            start.text += f'\n{a_week_ago}'
            end.text += f'\n{today}'
            _once.append(1)
        self.generate_trend()

    def on_name_entered_in_add_entry_screen(self, c: str, *args):
        text_field = self.root.ids.entry_add_screen.ids.meal_name_input
        target = text_field.text + c
        if self._drop_down:
            self._drop_down.dismiss()
        self._drop_down = MDDropdownMenu(
            caller=text_field,
            width_mult=4)

        def callback(txt: str) -> None:
            self.root.ids.entry_add_screen.ids.meal_name_input.text = txt
            with MealDB() as db:
                self.root.ids.entry_add_screen.ids.grams_input.text = str(db.get_meal_by_name(txt).portion)
            if self._drop_down:
                self._drop_down.dismiss()

        with MealDB() as mdb:
            names = sort_by_similarity(mdb.get_all_meal_names(), target)
            for name in names[:5]:
                self._drop_down.items.append({'viewclass': 'OneLineListItem',
                                              'text': f'[font=Arial]{name}[/font]',
                                              'on_release': lambda txt=name: callback(txt)
                                              })

        self._drop_down.open()
        return c

    def on_submit_meal_entry(self, *args):
        name = self.root.ids.entry_add_screen.ids.meal_name_input.text
        portion = self.root.ids.entry_add_screen.ids.grams_input.text
        entry_date = self.root.ids.entry_add_screen.ids.date_input.text.splitlines()[-1]
        dialog = None
        with MealDB() as mdb:
            names = mdb.get_all_meal_names()
        if name not in names:
            def open_plus_dialog(*_):
                print(_)
                dialog.dismiss()
                d = MealAddDialog(self)
                d.meal_name.text, d.title = name, f'"{name}" not in Meals, Please add it below:'
                d.open()

            def start_search(*_):
                print(_)
                dialog.dismiss()
                self.on_search_meal_pressed(name)

            dialog = MDDialog(title=f'"{name}" not in Meals',
                              text='Try One of the options below:',
                              buttons=[
                                  MDFillRoundFlatIconButton(text="Search", icon='magnify',
                                                            on_press=start_search),
                                  MDFillRoundFlatIconButton(text="Add new", icon='plus',
                                                            on_press=open_plus_dialog)
                              ])
            dialog.open()
        else:
            with MealEntriesDB() as me_db:
                me = MealEntry(name=name, portion=float(portion or 0), date=entry_date)
                me_db.add_meal_entry(me)
                toast(f'Added Meal entry!\n({me}')

    def on_delete_meals_pressed(self, *args):
        names = [x[0] for x in self.meals_table.get_row_checks()]
        names = [x.strip('[font=Arial]').strip('[/font]') for x in names]

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
    def show_date_picker(button, is_limited: bool = True, *args, **kwargs):
        """Helper function for binding a button with a date it displays.
        Preferably the text of the button should be set to "Date:" in .kv file. """

        def got_date(_, _date, *a, **k):
            button.text = button.text.splitlines()[0] + '\n' + _date.isoformat()

        if is_limited:
            with MealEntriesDB() as me_db:
                first, last = me_db.get_first_last_dates()
            if first == last:
                first -= timedelta(days=1)
            picker = MDDatePicker(min_date=first, max_date=last)
        else:
            picker = MDDatePicker()

        picker.bind(on_save=got_date)
        picker.open()

    def set_trends_date_range(self, days_back: int):
        """Callback for binding event to setting trends date range."""
        end_date = dt.now().date()
        start_date = end_date - timedelta(days=days_back)
        start_button = self.root.ids.trends_screen.ids.trend_start_date_button
        end_button = self.root.ids.trends_screen.ids.trend_end_date_button
        start_button.text = "\n".join((start_button.text.splitlines()[0], start_date.isoformat()))
        end_button.text = "\n".join((end_button.text.splitlines()[0], end_date.isoformat()))

    def generate_trend(self, *args, **kwargs):
        # -- Getting The relevant entries
        start_date = self.root.ids.trends_screen.ids.trend_start_date_button.text.splitlines()[-1]
        end_date = self.root.ids.trends_screen.ids.trend_end_date_button.text.splitlines()[-1]

        with MealEntriesDB() as me_db:
            entries = me_db.get_entries_between_dates(str(start_date), str(end_date))

        trends_layout = self.root.ids.trends_screen.ids.trends_layout
        trends_layout.clear_widgets()
        # -- Adding Graph of calorie sum
        data = dict.fromkeys((e.date for e in entries), 0)
        for e in entries:
            data[e.date] += e.meal.cals

        graph = plot_graph(data, y_label='Calories')
        trends_layout.add_widget(graph)

        # -- Adding Graph of sodium
        data = dict.fromkeys((e.date for e in entries), 0)
        for e in entries:
            data[e.date] += e.meal.sodium
        graph = plot_graph(data, y_label='Sodium')
        trends_layout.add_widget(graph)

        # -- Adding Pie Chart
        data = {
            'Protein': sum(e.meal.proteins for e in entries),
            'Carbs': sum(e.meal.carbs for e in entries),
            'Fats': sum(e.meal.fats for e in entries)
        }
        pie_chart = plot_pie_chart(data)
        trends_layout.add_widget(pie_chart)

    def on_search_meal_pressed(self, query: str = '', *args, **kwargs):
        """ Search for a meal button pressed. """
        self.root.transition.direction = 'left'
        self.root.current = 'meal_search_screen'
        if query:
            self.meal_search_screen.search_input_field.text = query

    def show_theme_picker(self, *args, **kwargs):

        def _set_theme(*a, **k):
            parser = configparser.ConfigParser()
            parser[THEME] = {
                'theme_style': self.theme_cls.theme_style,
                'primary_palette': self.theme_cls.primary_palette,
                'accent_palette': self.theme_cls.accent_palette,
            }
            with open(CONFIG, 'w+') as fl:
                parser.write(fl)

        theme_dialog = MDThemePicker()
        theme_dialog.bind(on_dismiss=_set_theme)
        theme_dialog.open()


if __name__ == '__main__':
    CaloriesApp().run()
