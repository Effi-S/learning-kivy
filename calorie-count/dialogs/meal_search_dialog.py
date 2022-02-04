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
from dialogs.meal_add_dialog import MealAddDialog
from utils import RTLMDTextField


class MealSearchDialog(MDDialog):
    """A dialog/pop-up asking the user to search for a new Meal."""

    def __init__(self, app, **kwargs):
        self.app = app
        # dialog buttons
        self.root_window = app.root_window
        self.return_button = MDFillRoundFlatIconButton(text="Return", icon="undo",
                                                       on_press=self.dismiss)
        # content
        self.content = MDBoxLayout(orientation="vertical",
                                   size_hint_y=None,
                                   height=self.root_window.height * .6)

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
        results_scroll = ScrollView(size_hint_y=None,
                                    height=self.root_window.height * .6
                                    )
        self.list_results = MDList()
        results_scroll.add_widget(self.list_results)
        self.content.add_widget(results_scroll)

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
                tertiary = f'Protein: {food.protein}, Fat: {food.fats}, Carbs: {food.carbs}\n' \
                           f' Sodium: {food.sodium}, Sugar: {food.sugar}, Water: {food.water}'
                list_item = ThreeLineAvatarListItem(text=title, secondary_text=",".join(desc), tertiary_text=tertiary)
                list_item.add_widget(IconLeftWidget(icon=_icon_from_food(food)))
                list_item.bind(on_press=lambda *a, f=food, **k: self.add_food(f))
                self.list_results.add_widget(list_item)

    def add_food(self, food: FoodData):
        self.dismiss()
        dialog = MealAddDialog(self.app)
        title, *desc = food.description.split(',')
        dialog.meal_name.text = str(title)
        dialog.protein.text = str(food.protein)
        dialog.fats.text = str(food.fats)
        dialog.carbs.text = str(food.carbs)
        dialog.salt.text = str(food.sodium)
        dialog.sugar.text = str(food.sugar)
        dialog.water.text = str(food.water)
        dialog.open()


