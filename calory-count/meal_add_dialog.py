from __future__ import annotations
from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

from DB.meal_db import MealDB, Meal


class MealAddDialog(MDDialog):
    last_submission: Meal = None  # Here we can store the last Meal submission
    def __init__(self, root_window, allow_nameless: bool = False, **kwargs):

        self.allow_nameless = allow_nameless
        # dialog buttons
        self.root_window = root_window
        self.submit_button = MDFillRoundFlatIconButton(text="Submit Meal", icon="basket-plus",
                                                       on_press=self.on_submit_meal_button_pressed)
        self.clear_button = MDFillRoundFlatIconButton(text="Clear selection", icon="undo",
                                                      on_press=self.on_clear_meal_button_pressed)
        # content
        self.content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=self.root_window.height * .6)

        # meal name
        self.meal_name = MDTextField(hint_text="Enter name of the meal", icon_right="food-variant")
        self.content.add_widget(self.meal_name)

        # accumulative/percent switch
        inner_content = MDBoxLayout(orientation="horizontal", size_hint=(1, .2))
        self.is_percent_label = MDLabel(text='Percentage(%)/Accumulative(g)')
        self.is_percent_switch = MDSwitch(on_touch_up=self._on_percent_switch_touch_up,
                                          pos_hint={'y': .05})
        inner_content.add_widget(self.is_percent_label)
        inner_content.add_widget(self.is_percent_switch)
        self.content.add_widget(inner_content)

        # meal portion
        self.meal_portion = MDTextField(hint_text="Enter Portion (g) of the meal", icon_right="scale")

        # fourth line - text fields
        def only_number(s: str, *args):
            """Filter function for MDTextFields that can only have numbers as input."""
            if not s.isnumeric():
                toast('Only numbers!')
                return ''
            return s

        inner_content = MDBoxLayout(orientation="horizontal")
        self.protein = MDTextField(hint_text="Proteins (g)", icon_right='food-steak', input_filter=only_number)
        self.fats = MDTextField(hint_text="Fats (g)", icon_right='fish', input_filter=only_number)
        self.carbs = MDTextField(hint_text="Carbs (g)", icon_right='pasta', input_filter=only_number)
        for x in (self.protein, self.fats, self.carbs):
            inner_content.add_widget(x)
        self.content.add_widget(inner_content)

        # fifth line - more text fields
        self.sugar = MDTextField(hint_text="Sugar (g)", icon_right='food-apple', input_filter=only_number)
        self.salt = MDTextField(hint_text="Salt (mg)", icon_right='shaker', input_filter=only_number)
        inner_content = MDBoxLayout(orientation="horizontal")
        for x in (self.salt, self.sugar):
            inner_content.add_widget(x)
        self.content.add_widget(inner_content)

        # building the dialog
        super().__init__(title='Add A new Meal', type='custom',
                         content_cls=self.content,
                         buttons=[self.submit_button, self.clear_button],
                         **kwargs)

    def check_errors(self) -> list[str]:
        """ Make sure input is ok before adding meal to DB"""
        errors = []
        sum_inputs = self._sum_inputs()

        if self.is_percent_switch.active:
            if sum_inputs > 100:
                errors.append(f'Sum of inputs exceeds 100% ({sum_inputs}%)')

        if not self.allow_nameless and not self.meal_name.text:
            errors.append('No Meal Name was entered')

        if self.meal_name.text:
            with MealDB() as mdb:
                if self.meal_name.text in mdb.get_all_meal_names():
                    errors.append(f'Name: {self.meal_name.text} already exists!')
        return errors

    def _sum_inputs(self):
        """Get the sum in grams of all of the text fields of the dialog that receive."""
        gram_inputs = (self.protein, self.fats, self.carbs, self.sugar)
        mg_inputs = (self.salt,)
        sum_grams = sum(int(x.text) for x in gram_inputs if x.text)
        sum_mg = sum(int(x.text) / 1000 for x in mg_inputs if x.text)
        return sum_grams + sum_mg

    def on_submit_meal_button_pressed(self, *args):
        """When A meal is submitted:
            1. Check for errors
            2. If no errors ad meal to DB (otherwise toast)"""
        errors = self.check_errors()
        if errors:
            toast('\n'.join(errors))
        else:
            portion = 100 if self.is_percent_switch.active else self._sum_inputs()
            with MealDB() as mdb:
                meal = Meal(name=self.meal_name.text,
                            portion=portion,
                            proteins=int(self.protein.text),
                            fats=int(self.fats.text),
                            carbs=int(self.carbs.text),
                            sugar=int(self.sugar.text),
                            sodium=int(self.salt.text))
                mdb.add_meal(meal)
                self.last_submission = meal
                toast(f'Meal {meal.name} added!')

    def on_clear_meal_button_pressed(self, *args):
        """Clear all the selections."""
        for x in (self.meal_name, self.meal_portion, self.protein, self.fats,
                  self.carbs, self.salt, self.sugar):
            x.text = ''

    def _on_percent_switch_touch_up(self, *args):
        """Swapping from accumulative to percent method."""
        inputs = (self.protein, self.fats, self.carbs, self.salt, self.sugar)
        if self.is_percent_switch.active:
            if not self.meal_portion.parent:
                self.content.add_widget(self.meal_portion, index=3)
            self.is_percent_label.text = 'Percentage(%)'
            for x in inputs:
                x.hint_text = x.hint_text.replace('(g)', '(%)').replace('(mg)', '(mg/100g)')
        else:
            self.is_percent_label.text = 'Accumulative(g)'
            if self.meal_portion.parent:
                self.content.remove_widget(self.meal_portion)
            for x in inputs:
                x.hint_text = x.hint_text.replace('(%)', '(g)').replace('(mg/100g)', '(mg)')
