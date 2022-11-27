""" Here we store Excel utilities """
from dataclasses import astuple

import openpyxl
from kivymd.toast import toast

from DB.food_db import FoodDB
from DB.meal_entry_db import MealEntriesDB

DEFAULT_XLSX = 'Calorie_Counting.xlsx'
FOOD_SHEET = 'My Foods'
MEALS_SHEET = 'My Meal Entries'


def save_to_excel(path: str = DEFAULT_XLSX, *args) -> None:
    """Save Foods and entries to xlsx file
    The file will have 2 sheets: 'My Foods' and 'My Meal Entries'"""
    wb = openpyxl.Workbook()

    # --1-- Creating Foods sheet
    wb.active.title = FOOD_SHEET
    with FoodDB() as fdb:
        foods = fdb.get_all_foods()
    if foods:
        wb.active.append(foods[0].columns())
        for food in foods:
            wb.active.append(food.values)

    # --2-- Creating meals sheet
    sh = wb.create_sheet(MEALS_SHEET)
    with MealEntriesDB() as mdb:
        start, end = map(str, mdb.get_first_last_dates())
        entries = mdb.get_entries_between_dates(start, end)
        print(entries)
    if entries:
        sh.append(entries[0].columns())
        for entry in entries:
            sh.append(entry.values)

    # --3-- Saving Workbook
    print(f'Saving file here:', path)
    wb.save(path)


def import_excel(path: str = DEFAULT_XLSX, *args) -> None:
    toast('Not implemented yet')


# save_to_excel()
