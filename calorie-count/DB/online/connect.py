from __future__ import annotations

import atexit
import sqlite3
import os
from dataclasses import dataclass


@dataclass
class FoodData:
    """This class represents a Searchable Food """
    description: str
    portions: dict[str, float]  # Maps a portion name to grams. example: '1 cup' -> 30 (g)
    # -- The following represent grams out of 100g
    protein: float
    fats: float
    carbs: float
    sodium: float
    sugar: float
    water: float


class ExternalFoodsDB:
    def __init__(self):
        self.conn = sqlite3.connect('DB/online/external_foods.db')
        atexit.register(lambda: self.conn.close())  # In-case 'with' not used
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE if not exists foods(
                                description text,
                                portions text,
                                protein real,
                                fats real,
                                carbs real,
                                sodium real,
                                sugar real,
                                water real
                            )''')
        self.conn.commit()
        self.cursor.execute('''CREATE TABLE if not exists portions(
                                name text, 
                                grams real
                            ''')
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self

    def __exit__(self):
        self.conn.close()
