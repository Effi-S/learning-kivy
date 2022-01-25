from datetime import date, timedelta
from datetime import datetime as dt
from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconRightWidget

from DB.meal_entry_db import MealEntriesDB, MealEntry


class ListEntry(TwoLineAvatarIconListItem):
    """TwoLineAvatarIconListItem with delete Icon"""

    def __init__(self, entry_list: MDList, entry: MealEntry, **kwargs):
        self.entry_list = entry_list
        self.entry_id = entry.id
        self.delete_icon = IconRightWidget(icon='delete', on_release=self.on_del_icon_pressed)
        self.is_icon_hidden = True
        super().__init__(**kwargs, on_press=lambda *a, **k: self.on_item_press(self.entry_id , *a, **k))

    def on_item_press(self, entry_id: str, _item: TwoLineAvatarIconListItem, *a, **k):
        """Callback for when list item pressed (Note: mutable default on purpose)"""
        if not self.is_icon_hidden:
            return

        def _revert(*_a, **_k):
            """Callback for returning back to normal."""
            self.delete_icon.parent.remove_widget(self.delete_icon)
            self.is_icon_hidden = True

        self.add_widget(self.delete_icon)
        self.is_icon_hidden = False
        Clock.schedule_once(_revert, 5)

    def on_del_icon_pressed(self, icon: IconRightWidget, *_a, **_k):
        """Callback for when delete icon on list item pressed."""
        self.entry_list.remove_widget(self)
        with MealEntriesDB() as db:
            db.delete_entry(self.entry_id)
        toast(f'{self.text} Removed')




def init_daily_screen(app, day: date = dt.now().date()):
    """Given the App (as reference), clears and re-loads the Daily screen.
     Loads the Entries based on the date given. Default date is today"""

    # -- Set label
    today, one_day = dt.now().date(), timedelta(days=1)
    day_lbl = 'Today' if day == today else 'Yesterday' if day == today - one_day else day.isoformat()
    app.root.ids.total_cals_header_label.text = f'Total Calories {day_lbl}'

    # -- Set Sum
    with MealEntriesDB() as me_db:
        entries = me_db.get_entries_between_dates(day.isoformat(), day.isoformat())
    cals = sum(e.meal.cals for e in entries)
    app.root.ids.total_cals_label.text = f'{cals: .2f}'

    # -- Create List of Entries
    entry_list: MDList = app.root.ids.daily_entries_list
    entry_list.clear_widgets()
    for i, entry in enumerate(entries, 1):
        entry_list.add_widget(ListEntry(entry_list, entry,
                                        text=entry.meal.name or f'Meal {i} (Unnamed)',
                                        secondary_text=f'Calories: {entry.meal.cals: .2f}'))


