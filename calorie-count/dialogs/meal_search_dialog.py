"""This Module holds a class MealAddDialog
    - The dialog/pop-up of our calorie App that asks the user to input a new meal."""
from __future__ import annotations
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFloatingActionButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog

from DB.external.client import ExternalFoodsDB
from utils import RTLMDTextField


class MealSearchDialog(MDDialog):
    """A dialog/pop-up asking the user to search for a new Meal."""

    def __init__(self, app, **kwargs):
        # dialog buttons
        self.root_window = app.root_window
        self.return_button = MDFillRoundFlatIconButton(text="Return", icon="undo",
                                                       on_press=self.dismiss)
        # content
        self.content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=self.root_window.height * .4)

        # Search Bar
        search_bar_layout = MDBoxLayout()
        self.search_input_field = RTLMDTextField(hint_text="Enter name of the meal to Search",
                                                 pos_hint={'center_y': 0.9},
                                                 mode='rectangle',
                                                 font_name='Arial')
        search_bar_layout.add_widget(self.search_input_field)

        search_button = MDFloatingActionButton(icon='magnify', text='Search',
                                               pos_hint={'center_y': 0.9},
                                               on_press=self.run_search,
                                               theme_text_color='Primary')
        search_bar_layout.add_widget(search_button)
        self.content.add_widget(search_bar_layout)

        # Search results
        self.results_layout = MDBoxLayout(orientation="horizontal", size_hint_y=0.9)
        self.content.add_widget(self.results_layout)

        # building the dialog
        super().__init__(type='custom',
                         content_cls=self.content,
                         buttons=[self.return_button],
                         **kwargs)

    def run_search(self, *args):
        """ Search for the desired meal """
        to_search = self.search_input_field.text
        if not to_search:
            return
        with ExternalFoodsDB() as ef_db:
            for food in ef_db.get_similar_food_by_name(to_search):
                print(food)
        print('run_search pressed:', to_search)
