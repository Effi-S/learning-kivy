import sqlite3
from dataclasses import dataclass

@dataclass
class Meal:
    name: str
    date: str
    proteins: float
    fats: float
    carbs: float
    grams: float
    cals: float

    @property
    def columns(self) -> list[str]:
        return list(self.__dict__.keys())
    @property
    def values(self) -> list[str]:
        return list(self.__dict__.values())

class MealDB:
    def __init__(self):
        # Connect to DB (or create one if none exists)
        self.conn = sqlite3.connect("meals")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE if not exists meals(
                          name text,
                          date text,
                          protein real,
                          fats real,
                          carbs real,
                          grams real,
                          calories real
                          )''')
        self.conn.commit()

    def __enter__(self, *a, **k):
        return self
    def __exit__(self, *a, **k):
        self.conn.close()

    def get_all_meals(self) -> list[Meal]:
        self.cursor.execute("SELECT * FROM meals")
        return [Meal(*x) for x in self.cursor.fetchall()]

    def add_meal(self, meal: Meal):
        self.cursor.execute(f'INSERT INTO meals Values {tuple(meal.values)}', meal.__dict__)
        self.conn.commit()
