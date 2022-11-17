""" Here we store Excel utilities """
from dataclasses import astuple

import openpyxl

from DB.food_db import FoodDB

FOOD_SHEET = 'My Foods'
MEALS_SHEET = 'My Meal Entries'


def save_to_excel(path: str = 'Calorie_Counting.xlsx'):
    """Save Foods and entries to xlsx file
    The file will have 2 sheets: 'My Foods' and 'My Meal Entries'"""
    wb = openpyxl.Workbook()

    # --1-- Creating Foods sheet
    wb.active.title = FOOD_SHEET
    with FoodDB() as fdb:
        foods = fdb.get_all_foods()
        print(foods)
        if foods:
            print('No Foods')
            data = [foods[0].columns()] + [food.values for food in foods]
            print(data)
            for row in data:
                wb.active.append(row)
    # --2-- Creating meals sheet
    sh = wb.create_sheet(MEALS_SHEET)

    # --3-- Saving Workbook
    print(f'Saving file here:', path)
    wb.save(path)
save_to_excel()