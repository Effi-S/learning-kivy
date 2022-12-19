"""This module holds a connection for our Meal-Entries Database "MealEntries"
Parameters to and from this DB are passed with instances of the  dataclass "MealEntry". """
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime as dt
from src.DB.food_db import Food, FoodDB
from src.utils import config
from src.utils.utils import str2iso


@dataclass
class MealEntry:
    """This dataclass represents the data in the MealEntries DB"""
    name: str = field(default=None)
    portion: float = field(default=None)
    date: str = field(default=None)
    food: Food = field(default=None)
    id: str = field(default=None)  # The ID is added only when the entry is added to the DB
    FOOD_DB_PATH: str = None  # init function for FoodDB

    def __post_init__(self):
        assert self.name or self.food, 'name or meal missing'
        if self.name and not self.food:
            with FoodDB(self.FOOD_DB_PATH) as fdb:
                self.food = fdb.get_food_by_name(self.name)
        if self.food and not self.name:
            # means nameless meal-entry
            with FoodDB(self.FOOD_DB_PATH) as fdb:
                fdb.add_food(food=self.food)
                print(f'Added to MealDB: {self.food}.')

        if not self.date:
            self.date = dt.now().date().isoformat()

        if not self.portion:
            self.portion = self.food.portion
        elif self.portion != self.food.portion:
            ratio = self.portion / self.food.portion
            self.food.carbs *= ratio
            self.food.fats *= ratio
            self.food.proteins *= ratio
            self.food.sodium *= ratio
            self.food.sugar *= ratio

    @staticmethod
    def columns() -> tuple[str, ...]:
        """The columns for displaying """
        return 'Date', 'Name', 'Portion (g)', 'Protein (g)', 'Fats (g)', 'Carbs (g)', 'Sugar (g)', 'Sodium (mg)', \
            'Water (g)', 'Calories'

    @property
    def values(self) -> tuple:
        return self.date, self.name, self.portion, self.food.proteins, self.food.fats, self.food.carbs, \
            self.food.sugar, self.food.sodium, self.food.water, self.food.cals


class MealEntryDB:
    MealEntry: MealEntry = MealEntry  # coupling MealEntry to MealEntryDB instance

    def __init__(self, db_path: str = None):
        if not db_path:
            db_path = config.get_db_path()
        self.MealEntry.FOOD_DB_PATH = db_path = config.get_db_path()

        # Connect to DB (or create one if none exists)
        self.conn = sqlite3.connect(db_path, timeout=15)
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
        cmd = f"INSERT INTO meal_entries Values ('{entry.food.id}', {entry.portion}, " \
              f"'{entry.date}', '{entry.id}')"
        print(cmd)
        self.cursor.execute(cmd, {'meal_id': entry.food.id,
                                  'portion': entry.portion,
                                  'date': entry.date,
                                  'id': entry.id})
        self.conn.commit()

    def get_entries_between_dates(self, start_date: str, end_date: str) -> list[MealEntry]:
        cmd = f'SELECT * FROM meal_entries WHERE date BETWEEN "{start_date}" AND "{end_date}"'
        self.cursor.execute(cmd)
        ret = []
        for entry in self.cursor.fetchall():
            with FoodDB() as fdb:
                meal_id, portion, date, e_id = entry
                meal = fdb.get_food_by_id(meal_id)
            ret.append(self.MealEntry(name=meal.name, food=meal, portion=portion, date=date, id=e_id))
        return ret

    def get_first_last_dates(self) -> tuple[dt.date, dt.date]:
        """Get the first and the last date of all entries"""

        cmd = f'SELECT MIN(date), MAX(date) FROM meal_entries'
        self.cursor.execute(cmd)
        start, end = self.cursor.fetchone()
        if not any((start, end)):
            today = str2iso(dt.now().date().isoformat())
            return today, today

        start, end = str2iso(start), str2iso(end)
        return start, end

    def delete_entry(self, time_stamp: str) -> None:
        """remove an entry based on it's id """
        cmd = 'DELETE FROM meal_entries ' \
              f"WHERE `id` = '{time_stamp}'"
        print(cmd)
        self.cursor.execute(cmd)
        self.conn.commit()
