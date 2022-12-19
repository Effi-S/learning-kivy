"""This module holds a connection for our Food Database "FoodDB"
Parameters to and from this DB are passed with instances of the  dataclass "Food". """
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field, astuple, asdict
from datetime import datetime as dt
from typing import Iterable, Any, Optional

from src.utils import config


@dataclass
class Food:
    """This dataclass represents a row in FoodDB"""
    name: str
    portion: float  # (g)
    proteins: float  # (g)
    fats: float  # (g)
    carbs: float  # (g)
    sugar: float  # (g)
    sodium: float  # (mg)
    water: float  # (g)
    id: str = field(default=None)

    def __post_init__(self):
        self.portion = self.portion or 0
        self.sodium = self.sodium or 0
        self.sugar = self.sugar or 0
        self.water = self.water or 0
        self.id = self.name or dt.now().isoformat()

    @property
    def cals(self):
        """Calculate the calories of the Food."""
        return self.proteins * 4 + self.carbs * 4 + self.fats * 9

    @staticmethod
    def columns() -> tuple[str, ...]:
        """Get all the column headers for representing a 'Food' to the customer."""
        return 'Name', 'Portion (g)', 'Protein (g)', 'Fats (g)', 'Carbs (g)', \
            'Sugar (g)', 'Sodium (mg)', 'Water (g)', 'Calories'

    @property
    def values(self) -> tuple[float, ...] | tuple[float | Any, ...]:
        """Get all the Values in the Food to represent to the customer."""
        return astuple(self)[:-1] + (self.cals,)  # everything but "id" + calories


class FoodDB:
    def __init__(self, db_path: str = None):
        db_path = db_path or config.get_db_path()
        # Connect to DB (or create one if none exists)
        self.conn = sqlite3.connect(db_path, timeout=15)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE if not exists food(
                                name text PRIMARY KEY,
                                portion real,
                                protein real,
                                fats real,
                                carbs real,
                                sugar real,
                                sodium real, 
                                water real,
                                id text
                            )''')
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self

    def __exit__(self, *a, **k):
        self.conn.close()

    def get_all_foods(self) -> list[Food]:
        self.cursor.execute("SELECT * FROM food")
        return [Food(*x) for x in self.cursor.fetchall() if x and x[0]]

    def get_all_food_names(self) -> list[str]:
        self.cursor.execute("SELECT name FROM food")
        return [str(x) for f in self.cursor.fetchall() for x in f if x]

    def get_food_by_name(self, name: str):
        cmd = f" SELECT * FROM food  WHERE `name` = '{name}'"
        self.cursor.execute(cmd)
        return Food(*(self.cursor.fetchone() or ()))

    def get_food_by_id(self, id_: str):
        cmd = f" SELECT * FROM food WHERE `id` = '{id_}'"
        self.cursor.execute(cmd)
        return Food(*self.cursor.fetchone())

    def add_food(self, food: Food, update: bool = False):
        """update => existing Foods are updated"""
        or_update = 'OR UPDATE' if update else ''
        cmd = f'INSERT {or_update} INTO food Values {astuple(food)}'
        self.cursor.execute(cmd, asdict(food))
        self.conn.commit()

    def remove(self, names: Optional[str, list[str]]) -> None:
        if isinstance(names, str):
            names = [names]
        if not names:
            return

        def it2str(tp: Iterable):
            """Helper function  - parses iterable to SQL string"""
            return '({})'.format(','.join(f"'{x}'" for x in tp))

        # -- CHECK FOR references in Entries
        cmd = f"""SELECT name FROM food
                    inner join meal_entries  
                  WHERE meal_entries.meal_id = food.id
                    AND name in {it2str(names)}"""
        self.cursor.execute(cmd)
        to_clear_name = [x for tp in self.cursor.fetchall() for x in tp]
        to_delete = [n for n in names if n not in to_clear_name]

        if to_delete:
            cmd = f"""DELETE FROM food 
                    WHERE `name` in {it2str(to_delete)};"""
            print(cmd)
            self.cursor.execute(cmd)
            self.conn.commit()

        if to_clear_name:
            cmd = f"""UPDATE food
                        SET name = ''
                      WHERE name in {it2str(to_clear_name)};"""
            print(cmd)
            self.cursor.execute(cmd)
            self.conn.commit()
