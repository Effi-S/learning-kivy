"""This module holds a connection for our Meals Database "MealBD"
Parameters to and from this DB are passed with instances of the  dataclass "Meal". """
from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field, astuple, asdict
from datetime import datetime as dt
from typing import Iterable


@dataclass
class Meal:
    """This dataclass represents the data in the Meal DB"""
    name: str
    portion: float   # (g)
    proteins: float  # (g)
    fats: float      # (g)
    carbs: float     # (g)
    sugar: float     # (g)
    sodium: float    # (mg)
    id: str = field(default=None)

    def __post_init__(self):
        self.id = self.name or dt.now().isoformat()

    @property
    def cals(self):
        """Calculate the calories of the Meal."""
        return ((self.proteins * 4 + self.carbs * 4 + self.fats * 9) / 100) * self.portion

    @staticmethod
    def columns() -> tuple[str, ...]:
        """Get all the column headers for representing a Meal to the customer."""
        return 'Name', 'Portion (g)', 'Protein (g)', 'Fats (g)', 'Carbs (g)', 'Sugar (g)', 'Sodium (mg)', 'Calories'

    @property
    def values(self) -> list[str]:
        """Get all the Values in the Meal to represent to the customer."""
        return astuple(self)[:-1] + (self.cals, )  # everything but "id" + calories


class MealDB:
    def __init__(self):
        # Connect to DB (or create one if none exists)
        self.conn = sqlite3.connect("calorie_app")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE if not exists meals(
                                name text,
                                portion real,
                                protein real,
                                fats real,
                                carbs real,
                                sugar real,
                                sodium real, 
                                id text
                            )''')
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self

    def __exit__(self, *a, **k):
        self.conn.close()

    def get_all_meals(self) -> list[Meal]:
        self.cursor.execute("SELECT * FROM meals")
        return [Meal(*x) for x in self.cursor.fetchall() if x and x[0]]

    def get_all_meal_names(self) -> list[str]:
        self.cursor.execute("SELECT name FROM meals")
        return [str(x) for f in self.cursor.fetchall() for x in f if x]

    def get_meal_by_name(self, name: str):
        self.cursor.execute(" SELECT * FROM meals"
                            f" WHERE `name` = '{name}'")
        return Meal(*self.cursor.fetchone())

    def get_meal_by_id(self, id_: str):
        self.cursor.execute(" SELECT * FROM meals"
                            f" WHERE `id` = '{id_}'")
        return Meal(*self.cursor.fetchone())

    def add_meal(self, meal: Meal):
        self.cursor.execute(f'INSERT INTO meals Values {astuple(meal)}', asdict(meal))
        self.conn.commit()

    def remove(self, names: list[str]) -> None:
        if not names:
            return

        def it2str(tp: Iterable):
            """Helper function  - parses iterable to SQL string"""
            return '({})'.format(','.join(f"'{x}'" for x in tp))

        # -- CHECK FOR references in Entries
        cmd = f"""SELECT name FROM meals
                    inner join meal_entries  
                  WHERE meal_entries.meal_id = meals.id
                    AND name in {it2str(names)}"""
        print(cmd)
        self.cursor.execute(cmd)
        to_clear_name = [x for tp in self.cursor.fetchall() for x in tp]
        to_delete = [n for n in names if n not in to_clear_name]

        if to_delete:
            cmd = f'DELETE FROM meals WHERE `name` in {it2str(to_delete)};'
            print(cmd)
            self.cursor.execute(cmd)
            self.conn.commit()

        if to_clear_name:
            cmd = f"""UPDATE meals
                        SET name = ''
                      WHERE name in {it2str(to_clear_name)};"""
            print(cmd)
            self.cursor.execute(cmd)
            self.conn.commit()
