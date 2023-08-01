"""This module holds a connection for our Food Database "FoodDB"
Parameters to and from this DB are passed with instances of the  dataclass "Food". """
from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy.orm import Session

from calorie_count.src.DB import base
from calorie_count.src.DB.orm import Food
from calorie_count.src.utils import config


class FoodDB:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.get_db_path()
        self.engine = base.create_engine(self.db_path)

    def __enter__(self, *a, **k):
        return self

    def __exit__(self, *a, **k):
        pass

    def get_all_foods(self) -> list[Food]:
        with Session(self.engine) as session:
            return session.query(Food).all()

    def get_all_food_names(self) -> list[str]:
        with Session(self.engine) as session:
            return session.get(Food.name).all()

    def get_food_by_name(self, name: str) -> Food:
        with Session(self.engine) as session:
            return session.query(Food).where(Food.name == name).first()

    def get_food_by_id(self, id_: str):
        with Session(self.engine) as session:
            return session.query(Food).where(Food.fid == id_).first()

    def add_food(self, food: Food):
        with Session(self.engine) as session:
            session.add(food)
            session.commit()
            session.refresh(food)
            return food

    def update_food(self, food: Food):
        f = self.get_food_by_name(food.name)
        with Session(self.engine) as session:
            f.update(food.__dict__)
            session.commit()

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
            self.conn.commit()
