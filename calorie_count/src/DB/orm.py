""" Here we will store SQLAlchemy ORMs """
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from calorie_count.src.DB.base import Base


class Table(StrEnum):
    FOOD = 'food'
    MEAL = 'meal'


class Food(Base):
    __tablename__ = Table.FOOD
    fid = sa.Column(sa.Uuid, index=True, primary_key=True,
                    unique=True, default=uuid.uuid4)
    name = sa.Column(sa.String(100), nullable=False,
                     default=datetime.utcnow)
    portion = sa.Column(sa.Float, nullable=False, default=100)
    proteins = sa.Column(sa.Float, nullable=False, default=0)
    fats = sa.Column(sa.Float, nullable=False, default=0)
    carbs = sa.Column(sa.Float, nullable=False, default=0)
    sugar = sa.Column(sa.Float, nullable=False, default=0)
    sodium = sa.Column(sa.Float, nullable=False, default=0)
    water = sa.Column(sa.Float, nullable=False, default=0)
    created = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    meals = relationship(back_populates='food')

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
        return (self.name,
                self.portion,
                self.proteins,
                self.fats,
                self.carbs,
                self.sugar,
                self.sodium,
                self.water,
                self.cals)

    def __init__(self, name, portion, protein, fats, carbs, sugar, sodium, water):
        self.name, self.portion, self.protein, self.fats, self.carbs, self.sugar, self.sodium, self.water = \
            name, portion, protein, fats, carbs, sugar, sodium, water

    def __int__(self, **kwargs):
        """SQLAlchemy Tables allow __init__ overloading like this."""
        self.__dict__.update(kwargs)

    def __repr__(self):
        return f"Food(name={self.name!r}, portion={self.portion!r}," \
               f" protein={self.protein!r}, fats={self.fats!r}, carbs={self.carbs!r}," \
               f" sugar={self.sugar!r}, sodium={self.sodium!r}, water={self.water!r}, calories={self.calories!r})"


class MealEntry(Base):
    __tablename__ = Table.MEAL.value
    mid = sa.Column(sa.Uuid, index=True, primary_key=True,
                    unique=True, default=uuid.uuid4)
    name = sa.Column(sa.String(100), nullable=False)
    portion: float = sa.Column(sa.Float, nullable=False)
    food_id = sa.ForeignKey(f'{Table.FOOD}.fid')
    food = relationship(back_populates='meals')
    date = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated = sa.Column(sa.DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __init__(self, name, portion, protein, fats, carbs, sugar, sodium, water):
        self.name, self.portion, self.protein, self.fats, self.carbs, self.sugar, self.sodium, self.water = \
            name, portion, protein, fats, carbs, sugar, sodium, water
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
        tp = tuple(sum(getattr(food, attr) for food in self.foods)
                   for attr in ('proteins', 'fats', 'carbs', 'sugar', 'sodium', 'water', 'cals')
                   )

        return self.date, self.name, self.portion, *tp

    def __repr__(self):
        return f'Meal(name={self.name!r}, portion={self.portion!r},' \
               f' foods={self.foods!r})'
