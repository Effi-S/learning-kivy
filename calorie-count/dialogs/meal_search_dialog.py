"""This Module holds a class MealAddDialog
    - The dialog/pop-up of our calorie App that asks the user to input a new meal."""
from __future__ import annotations

from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton, MDFloatingActionButton, MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import ThreeLineAvatarListItem, MDList, IconLeftWidget

from DB.external.client import ExternalFoodsDB, FoodData
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
        results_layout = MDBoxLayout(orientation="horizontal", pos_hint={'center_y': 0.9}, size_hint_y=0.9)
        results_scroll = ScrollView(pos_hint={'center_y': 0.9})
        results_layout.add_widget(results_scroll)
        self.list_results = MDList(pos_hint={'center_y': 0.9})
        results_scroll.add_widget(self.list_results)
        self.content.add_widget(results_layout)

        # building the dialog
        super().__init__(type='custom',
                         content_cls=self.content,
                         buttons=[self.return_button],
                         **kwargs)

    def run_search(self, *args):
        """ Search for the desired meal """

        def _icon_from_food(f: FoodData) -> str:
            """Helper function for finding the correct icon"""
            p, f, c = f.protein, f.fats, f.carbs
            if p > f and p > c:
                return 'food-steak'
            elif f > p and f > c:
                return 'fish'
            elif c > p and c > f:
                return 'noodles'
            return 'food'

        to_search = self.search_input_field.text
        if not to_search:
            return
        self.list_results.clear_widgets()
        with ExternalFoodsDB() as ef_db:
            for food in ef_db.get_similar_food_by_name(to_search):
                title, *desc = food.description.split(',')
                tertiary = f'Protein: {food.protein}, Fat: {food.fats}, Carbs: {food.carbs},' \
                           f' Sodium: {food.sodium}, Sugar: {food.sugar}, Water: {food.water}'
                list_item = ThreeLineAvatarListItem(text=title, secondary_text=",".join(desc), tertiary_text=tertiary)
                list_item.add_widget(IconLeftWidget(icon=_icon_from_food(food)))
                self.list_results.add_widget(list_item)
