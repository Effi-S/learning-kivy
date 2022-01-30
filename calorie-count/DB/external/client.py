from __future__ import annotations
import atexit
import os
import sqlite3
from dataclasses import dataclass, asdict, astuple
from typing import Generator
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    """Get similarity between 2 strings based on diff-lib's SequenceMatcher ratio"""
    return SequenceMatcher(None, str(a), str(b)).ratio()


@dataclass
class FoodData:
    """This class represents a Searchable Food """
    description: str
    portions: str  # string representation of mapping portion to quantity(g)  e.x - 'cup:30,bowl:100'...
    protein: float
    fats: float
    carbs: float
    sodium: float
    sugar: float
    water: float
    
    def __post_init__(self):
        self.description = self.description.replace('"', '')

    def portions_dict(self) -> dict[str, float]:
        return {a: b for x in ','.split(self.portions) for a, b in ':'.split(x)}


class ExternalFoodsDB:
    def __init__(self, locally: bool = False):
        db = 'DB/external/external_foods'
        if locally:
            db = 'external_foods'
        self.conn = sqlite3.connect(db)
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
        self.conn.create_function('edit_dist', 2, similarity)
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self

    def __exit__(self, *a, **k):
        self.conn.close()

    def add_food(self, food: FoodData):
        """Here we add a Food, parsed from an external API/JSON into ExternalFoodsDB."""
        cmd = f'INSERT INTO foods Values {astuple(food)}'
        print(cmd, asdict(food))
        self.cursor.execute(cmd, asdict(food))
        self.conn.commit()

    def get_similar_food_by_name(self, name: str, max_results: int = 5) -> Generator[FoodData]:
        """Given a name of a food return the most similar food in the DB.
        Ordered most similar to least similar.
        By default maximum of 5 values in the list, override 'max_results' to change this.

        Algorithm of similarity:
            1. Get foods where the given name is contained in the description.
            2. If none found in 1. -  iterate row-by-row running edit-distance on them
            add those that are > 0.9 ration.
            (Note: SQLite has 'editdist3' but I don't think it can work on android) """
        self.cursor.execute(f"SELECT * FROM foods WHERE description LIKE '%{name}%'")
        count = 0
        for _, row in zip(range(max_results), self.cursor):
            food = FoodData(*row)
            yield food
            count += 1

        if count < max_results:
            self.cursor.execute(f"SELECT * FROM foods WHERE edit_dist(`description`,  '{name}') >= 0.9")
            for _, row in zip(range(max_results - count), self.cursor):
                food = FoodData(*row)
                yield food
