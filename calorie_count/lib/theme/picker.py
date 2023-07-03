"""
Components/Pickers
==================

.. seealso::

    `Material Design spec, Time picker <https://material.io/components/time-pickers>`_

    `Material Design spec, Date picker <https://material.io/components/date-pickers>`_

.. rubric:: Includes date, time and color picker.

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/picker-previous.png
    :align: center

`KivyMD` provides the following classes for use:

- MDTimePicker_
- MDDatePicker_
- MDThemePicker_

.. MDTimePicker:
MDTimePicker
------------

.. rubric:: Usage

.. code-block::

    from kivy.lang import Builder

    from kivymd.app import MDApp
    from kivymd.uix.picker import MDTimePicker

    KV = '''
    MDFloatLayout:

        MDRaisedButton:
            text: "Open time picker"
            pos_hint: {'center_x': .5, 'center_y': .5}
            on_release: app.show_time_picker()
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)

        def show_time_picker(self):
            '''Open time picker dialog.'''

            time_dialog = MDTimePicker()
            time_dialog.open()


    Test().run()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/MDTimePicker.png
    :align: center

Binding method returning set time
---------------------------------

.. code-block:: python

    def show_time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time)
        time_dialog.open()

    def get_time(self, instance, time):
        '''
        The method returns the set time.

        :type instance: <kivymd.uix.picker.MDTimePicker object>
        :type time: <class 'datetime.time'>
        '''

        return time

Open time dialog with the specified time
----------------------------------------

Use the :attr:`~MDTimePicker.set_time` method of the
:class:`~MDTimePicker.` class.

.. code-block:: python

    def show_time_picker(self):
        from datetime import datetime

        # Must be a datetime object
        previous_time = datetime.strptime("03:20:00", '%H:%M:%S').time()
        time_dialog = MDTimePicker()
        time_dialog.set_time(previous_time)
        time_dialog.open()

.. note:: For customization of the :class:`~MDTimePicker` class, see the
    documentation in the :class:`~BaseDialogPicker` class.

.. MDDatePicker:
MDDatePicker
------------

.. warning:: The widget is under testing. Therefore, we would be grateful if
    you would let us know about the bugs found.

Usage
-----

.. code-block:: python

    from kivy.lang import Builder

    from kivymd.app import MDApp
    from kivymd.uix.picker import MDDatePicker

    KV = '''
    MDFloatLayout:

        MDToolbar:
            title: "MDDatePicker"
            pos_hint: {"top": 1}
            elevation: 10

        MDRaisedButton:
            text: "Open time picker"
            pos_hint: {'center_x': .5, 'center_y': .5}
            on_release: app.show_date_picker()
    '''


    class Test(MDApp):
        def build(self):
            return Builder.load_string(KV)

        def on_save(self, instance, value, date_range):
            '''
            Events called when the "OK" dialog box button is clicked.

            :type instance: <kivymd.uix.picker.MDDatePicker object>;

            :param value: selected date;
            :type value: <class 'datetime.date'>;

            :param date_range: list of 'datetime.date' objects in the selected range;
            :type date_range: <class 'list'>;
            '''

            print(instance, value, date_range)

        def on_cancel(self, instance, value):
            '''Events called when the "CANCEL" dialog box button is clicked.'''

        def show_date_picker(self):
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
            date_dialog.open()


    Test().run()


.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/MDDatePicker.gif
    :align: center

Open date dialog with the specified date
----------------------------------------

.. code-block:: python

    def show_date_picker(self):
        date_dialog = MDDatePicker(year=1983, month=4, day=12)
        date_dialog.open()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/previous-date.png
    :align: center

You can set the time interval from and to the set date. All days of the week
that are not included in this range will have the status `disabled`.

.. code-block:: python

    def show_date_picker(self):
        date_dialog = MDDatePicker(
            min_date=datetime.date(2021, 2, 15),
            max_date=datetime.date(2021, 3, 27),
        )
        date_dialog.open()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/range-date.gif
    :align: center

The range of available dates can be changed in the picker dialog:

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/change-range-date.gif
    :align: center

Select year
-----------

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/select-year-date.gif
    :align: center

.. warning:: The list of years when opening is not automatically set
    to the current year.

You can set the range of years using the :attr:`~kivymd.uix.picker.MDDatePicker.min_year` and
:attr:`~kivymd.uix.picker.MDDatePicker.max_year` attributes:

.. code-block:: python

    def show_date_picker(self):
        date_dialog = MDDatePicker(min_year=2021, max_year=2030)
        date_dialog.open()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/min-max-year-date.png
    :align: center

Set and select a date range
---------------------------

.. code-block:: python

    def show_date_picker(self):
        date_dialog = MDDatePicker(mode="range")
        date_dialog.open()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/set-select-range-date.gif
    :align: center

.. MDThemePicker:
MDThemePicker
-------------

.. code-block:: python

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()

.. image:: https://github.com/HeaTTheatR/KivyMD-data/raw/master/gallery/kivymddoc/MDThemePicker.gif
    :align: center
"""

__all__ = ("MDThemePicker",)


from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import (
    OptionProperty, StringProperty,
)
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp

from kivymd.color_definitions import colors, palette
from kivymd.uix.behaviors import (
    FakeRectangularElevationBehavior,
    SpecificBackgroundColorBehavior,
)
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import BaseDialog
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase


class Tab(MDFloatLayout, MDTabsBase):
    """Class implementing content for a tab."""

Builder.load_string(
    """      
         
<ColorSelector>
    canvas:
        Color:
            rgba: root.rgb_hex(root.color_name)
        Ellipse:
            size: self.size
            pos: self.pos


<AccentColorSelector@ColorSelector>
    on_release: app.theme_cls.accent_palette = root.color_name


<PrimaryColorSelector@ColorSelector>
    on_release: app.theme_cls.primary_palette = root.color_name


<MDThemePicker>
    size_hint: None, None
    size: "284dp", "400dp"

    MDBoxLayout:
        orientation: "vertical"

        MDTabs:
            on_tab_switch: root.on_tab_switch(*args)
            
            Tab:
                id: theme_tab
                text: "Theme"
                title: "Theme"
                icon: "none"
                
                MDGridLayout:
                    id: primary_box
                    adaptive_size: True
                    spacing: "8dp"
                    padding: "12dp"
                    pos_hint: {"center_x": .5, "top": 1}
                    cols: 5
                    rows: 4

                MDFlatButton:
                    text: "CLOSE"
                    pos: root.width - self.width - 10, 10
                    on_release: root.dismiss()

            Tab:
                text: "Accent"
                title: "Accent"
                icon: "none"
                
                MDGridLayout:
                    id: accent_box
                    adaptive_size: True
                    spacing: "8dp"
                    padding: "12dp"
                    pos_hint: {"center_x": .5, "top": 1}
                    cols: 5
                    rows: 4

                MDFlatButton:
                    text: "CLOSE"
                    pos: root.width - self.width - 10, 10
                    on_release: root.dismiss()

            Tab:
                text: "Style"
                title: "Style"
                icon: "none"

                MDGridLayout:

                    adaptive_size: True
                    spacing: "8dp"
                    pos_hint: {"center_x": .5, "center_y": .5}
                    cols: 2
                    rows: 1

                    MDIconButton:
                        canvas:
                            Color:
                                rgba: 1, 1, 1, 1
                            Ellipse:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 1
                            Line:
                                width: 1.
                                circle: (self.center_x, self.center_y, sp(62))

                        user_font_size: "100sp"
                        on_release: app.theme_cls.theme_style = "Light"

                    MDIconButton:
                        canvas:
                            Color:
                                rgba: 0, 0.3, 1, 1
                            Ellipse:
                                size: self.size
                                pos: self.pos

                        on_release: app.theme_cls.theme_style = "Dark"
                        user_font_size: "100sp"

                MDFlatButton:
                    text: "CLOSE"
                    pos: root.width - self.width - 10, 10
                    on_release: root.dismiss()
""")


class ColorSelector(MDIconButton):
    color_name = OptionProperty("Indigo", options=palette)

    def rgb_hex(self, col):
        return get_color_from_hex(colors[col][self.theme_cls.accent_hue])


class MDThemePicker(
    BaseDialog,
    SpecificBackgroundColorBehavior,
    FakeRectangularElevationBehavior,
):
    def on_open(self):
        self.on_tab_switch(None, self.ids.theme_tab, None, None)

    def on_tab_switch(
            self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        if instance_tab.text == "Theme":
            if not self.ids.primary_box.children:
                for name_palette in palette:
                    self.ids.primary_box.add_widget(
                        Factory.PrimaryColorSelector(color_name=name_palette)
                    )
        if instance_tab.text == "Accent":
            if not self.ids.accent_box.children:
                for name_palette in palette:
                    self.ids.accent_box.add_widget(
                        Factory.AccentColorSelector(color_name=name_palette)
                    )


KV = '''
FloatLayout:

    MDRaisedButton:
        text: "Open teme picker"
        pos_hint: {'center_x': .5, 'center_y': .5}
        on_release: app.show_theme_picker()
'''


class Test(MDApp):
    def build(self):
        return Builder.load_string(KV)

    def show_theme_picker(self):
        """Open time picker dialog."""

        time_dialog = MDThemePicker()
        time_dialog.open()


if __name__ == '__main__':
    Test().run()
