"""This module holds a connection for our Meal-Entries Database "MealEntries"
Parameters to and from this DB are passed with instances of the  dataclass "MealEntry". """
from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field, InitVar, asdict
from datetime import datetime as dt, timedelta
from typing import Iterable
import atexit
from DB.meal_db import Meal, MealDB


@dataclass
class MealEntry:
    """This dataclass represents the data in the MealEntries DB"""
    name: str = field(default=None)
    portion: float = field(default=None)
    date: str = field(default=None)
    meal: Meal = field(default=None)
    id: str = field(default=None)  # The ID is added only when the entry is added to the DB

    def __post_init__(self):
        assert self.name or self.meal, 'name or meal missing'
        if self.name and not self.meal:
            with MealDB() as mdb:
                self.meal = mdb.get_meal_by_name(self.name)
        if self.meal and not self.name:
            # means nameless meal-entry
            with MealDB() as mdb:
                mdb.add_meal(meal=self.meal)
                print(f'Added to MealDB: {self.meal}.')

        if not self.date:
            self.date = dt.now().date().isoformat()

        if not self.portion:
            self.portion = self.meal.portion
        elif self.portion != self.meal.portion:
            ratio = self.portion / self.meal.portion
            self.meal.carbs *= ratio
            self.meal.fats *= ratio
            self.meal.proteins *= ratio
            self.meal.sodium *= ratio
            self.meal.sugar *= ratio
            print(ratio, self)

    @staticmethod
    def columns() -> tuple[str, ...]:
        """The columns for displaying """
        return 'Name', 'Date', 'Portion (g)', 'Protein (g)', 'Fats (g)',


class MealEntriesDB:
    def __init__(self):
        # Connect to DB (or create one if none exists)
        self.conn = sqlite3.connect("calorie_app", timeout=15)
        atexit.register(lambda: self.conn.close)  #  for when 'with' not used
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE if not exists meal_entries(
                          meal_id text,
                          portion real,
                          date text,
                          id text
                          )''')
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self

    def __exit__(self, *a, **k):
        self.conn.close()

    def add_meal_entry(self, entry: MealEntry):
        entry.id = dt.now().isoformat()
        self.cursor.execute(f"INSERT INTO meal_entries Values ('{entry.meal.id}', {entry.portion}, "
                            f"'{entry.date}', '{entry.id}')",
                            {'meal_id': entry.meal.id, 'portion': entry.portion, 'date': entry.date, 'id': entry.id})
        self.conn.commit()

    def get_entries_between_dates(self, start_date: str, end_date: str) -> list[MealEntry]:
        cmd = f'SELECT * FROM meal_entries WHERE date BETWEEN "{start_date}" AND "{end_date}"'
        self.cursor.execute(cmd)
        ret = []
        for entry in self.cursor.fetchall():
            with MealDB() as mdb:
                meal_id, portion, date, e_id = entry
                meal = mdb.get_meal_by_id(meal_id)
                ret.append(MealEntry(name=meal.name, meal=meal, portion=portion, date=date, id=e_id))
        return ret

    def get_first_last_dates(self) -> tuple[dt.date, dt.date]:
        """Get the first and the last date of all entries"""
        def _str2iso(string):
            """Helper function turning strings to iso format date objects"""
            return dt.strptime(string, '%Y-%m-%d').date()

        cmd = f'SELECT MIN(date), MAX(date) FROM meal_entries'
        self.cursor.execute(cmd)
        start, end = self.cursor.fetchone()
        if not any((start, end)):
            today = _str2iso(dt.now().date().isoformat())
            return today, today

        start, end = _str2iso(start) - timedelta(days=1),  _str2iso(end)
        return start, end

    def delete_entry(self, time_stamp: str) -> None:
        """remove an entry based on it's id """
        cmd = 'DELETE FROM meal_entries ' \
              f"WHERE `id` = '{time_stamp}'"
        self.cursor.execute(cmd)
        self.conn.commit()

