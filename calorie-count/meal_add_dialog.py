"""This Module holds a class MealAddDialog
    - The dialog/pop-up of our calorie App that asks the user to input a new meal."""
from __future__ import annotations

import re

from kivymd.toast import toast
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

from DB.meal_db import MealDB, Meal


class FloatMDTextField(MDTextField):
    """TextField Input that only allows float input (0-9 or single dot)."""

    def insert_text(self, s, from_undo=False):
        if not s.isnumeric():
            if s != '.' or '.' in self.text:
                toast('Only numbers!')
                s = ''
        return super().insert_text(s, from_undo=from_undo)


class RTLMDTextField(MDTextField):
    """TextField Input that allows rtl."""
    _reg = re.compile(r'[a-zA-Z]')

    def insert_text(self, s, from_undo=False):
        if s.isalpha() and not self._reg.findall(s):
            self.text = s + self.text
            return super().insert_text('', from_undo=from_undo)
        return super().insert_text('s', from_undo=from_undo)


class MealAddDialog(MDDialog):
    """A dialog/pop-up asking the user to add a new Meal."""
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
        self.content = MDBoxLayout(orientation="vertical", size_hint_y=None, height=self.root_window.height * .4)

        # meal name
        self.meal_name = RTLMDTextField(hint_text="Enter name of the meal",
                                        font_name='Arial', icon_right="food-variant")
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

        inner_content = MDBoxLayout(orientation="horizontal")
        self.protein = FloatMDTextField(hint_text="Proteins (g)", icon_right='food-steak')
        self.fats = FloatMDTextField(hint_text="Fats (g)", icon_right='fish')
        self.carbs = FloatMDTextField(hint_text="Carbs (g)", icon_right='pasta')
        for x in (self.protein, self.fats, self.carbs):
            inner_content.add_widget(x)
        self.content.add_widget(inner_content)

        # fifth line - more text fields
        self.sugar = FloatMDTextField(hint_text="Sugar (g)", icon_right='food-apple')
        self.salt = FloatMDTextField(hint_text="Salt (mg)", icon_right='shaker')
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

        if not all((self.protein.text, self.fats.text, self.carbs)):
            errors.append('Must enter Protein Fats and Carbs!')

        if self.is_percent_switch.active:
            if sum_inputs > 100:
                errors.append(f'Sum of inputs exceeds 100% ({sum_inputs}%)')
            if not self.meal_portion.text:
                self.meal_portion.text = '100'

        if not self.allow_nameless and not self.meal_name.text:
            errors.append('No Meal Name was entered')

        if self.meal_name.text:
            with MealDB() as mdb:
                if self.meal_name.text in mdb.get_all_meal_names():
                    errors.append(f'Name: {self.meal_name.text} already exists!')
        return errors

    def _sum_inputs(self) -> float:
        """Get the sum in grams of all of the text fields of the dialog that receive."""
        gram_inputs = (self.protein, self.fats, self.carbs, self.sugar)
        mg_inputs = (self.salt,)
        sum_grams = sum(float(x.text) for x in gram_inputs if x.text)
        sum_mg = sum(float(x.text) / 1000 for x in mg_inputs if x.text)
        return sum_grams + sum_mg

    def on_submit_meal_button_pressed(self, *args):
        """When A meal is submitted:
            1. Check for errors
            2. If no errors ad meal to DB (otherwise toast)"""
        errors = self.check_errors()
        if errors:
            toast('\n'.join(errors))
            return

        if self.is_percent_switch.active:
            portion = float(self.meal_portion.text)
            self.protein.text = (float(self.protein.text) / 100) * portion
            self.fats.text = (float(self.fats.text) / 100) * portion
            self.carbs.text = (float(self.carbs.text) / 100) * portion
        else:
            portion = float(self._sum_inputs())

        with MealDB() as mdb:
            meal = Meal(name=self.meal_name.text,
                        portion=portion,
                        proteins=float(self.protein.text),
                        fats=float(self.fats.text),
                        carbs=float(self.carbs.text),
                        sugar=float(self.sugar.text or 0),
                        sodium=float(self.salt.text or 0))
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
