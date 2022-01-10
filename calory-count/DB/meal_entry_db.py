"""This module holds a connection for our Meal-Entries Database "MealEntries"
Parameters to and from this DB are passed with instances of the  dataclass "MealEntry". """
from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field, InitVar, asdict
from datetime import datetime as dt
from typing import Iterable

from DB.meal_db import Meal, MealDB


@dataclass
class MealEntry:
    """This dataclass represents the data in the MealEntries DB"""
    name: str = field(default=None)
    portion: float = field(default=None)
    date: str = field(default=None)
    meal: Meal = field(default=None)

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
        self.conn = sqlite3.connect("calorie_app")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE if not exists meal_entries(
                          meal_id text,
                          portion real,
                          date text
                          )''')
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self

    def __exit__(self, *a, **k):
        self.conn.close()

    def add_meal_entry(self, entry: MealEntry):
        self.cursor.execute(f"INSERT INTO meal_entries Values ('{entry.meal.id}', {entry.portion}, '{entry.date}')",
                            {'meal_id': entry.meal.id, 'portion': entry.portion, 'date': entry.date})
        self.conn.commit()

    def get_entries_between_dates(self, start_date: str, end_date: str) -> list[MealEntry]:
        cmd = f'SELECT * FROM meal_entries WHERE date BETWEEN "{start_date}" AND "{end_date}"'
        self.cursor.execute(cmd)
        ret = []
        for entry in self.cursor.fetchall():
            with MealDB() as mdb:
                meal_id, portion, date = entry
                meal = mdb.get_meal_by_id(meal_id)
                ret.append(MealEntry(name=meal.name, meal=meal, portion=portion, date=date))
        return ret

