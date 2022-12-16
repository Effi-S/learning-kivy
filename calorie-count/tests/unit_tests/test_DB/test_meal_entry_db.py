import os
import unittest
import uuid
from src.DB.food_db import FoodDB, Food
from src.DB.meal_entry_db import MealEntry, MealEntryDB
from src.utils import config


class TestFoodDB(unittest.TestCase):

    def setUp(self):
        # Create a new instance of FoodDB for each test method
        config.set_db_path_test()
        with FoodDB():  # So table will exist as well
            pass

        super().setUpClass()

    def test_add_meal_entry(self):
        with FoodDB() as fdb:  # So table will exist as well
            fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
            assert fdb.get_all_foods(), 'No foods'
        # Test adding a new meal entry
        entry = MealEntry(name="apple", date="2022-12-15", portion=100)
        print(entry)
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(entry)
            # Check that the entry was added to the database
            self.assertEqual(len(mdb.get_entries_between_dates("2022-12-14", "2022-12-16")), 1)

    def test_delete_entry(self):
        with FoodDB() as fdb:  # So table will exist as well
            fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
        # Test deleting a meal entry
        entry = MealEntry(name="apple", date="2022-12-15", portion=100)
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(entry)
            self.assertEqual(len(mdb.get_entries_between_dates("2022-12-15", "2022-12-15")), 1)
            mdb.delete_entry(entry.id)
            # Check that the entry was deleted from the database
            self.assertEqual(len(mdb.get_entries_between_dates("2022-12-15", "2022-12-15")), 0)

    def test_get_first_last_dates(self):
        with FoodDB() as fdb:  # So table will exist as well
            fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
            fdb.add_food(Food('banana', 100, 0.5, 0.2, 10, 4, 0, 86))
        # Test getting the first and last dates in the database
        entry1 = MealEntry(name="apple", date="2022-12-15", portion=100)
        entry2 = MealEntry(name="banana", date="2022-12-16", portion=100)
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(entry1)
            mdb.add_meal_entry(entry2)
            first_date, last_date = mdb.get_first_last_dates()
            # Check that the first and last dates in the database are as expected
            self.assertEqual(first_date, "2022-12-15")
            self.assertEqual(last_date, "2022-12-16")

    def test_get_entries_between_dates(self):
        # Create a MealEntryDB instance and add some MealEntry objects to it
        meal_entry_db = MealEntryDB()
        with FoodDB() as fdb:  # So table will exist as well
            fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
            fdb.add_food(Food('banana', 100, 0.5, 0.2, 10, 4, 0, 86))
            fdb.add_food(Food('orange', 100, 0.5, 0.2, 10, 4, 0, 86))
        meal_entry1 = MealEntry(name='apple', date='2022-01-01')
        meal_entry2 = MealEntry(name='banana', date='2022-01-02')
        meal_entry3 = MealEntry(name='orange', date='2022-01-03')
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(meal_entry1)
            mdb.add_meal_entry(meal_entry2)
            mdb.add_meal_entry(meal_entry3)
            # Verify expected list of MealEntry
            start_date = '2022-01-02'
            end_date = '2022-01-03'
            expected_entries = [meal_entry2, meal_entry3]
            assert meal_entry_db.get_entries_between_dates(start_date, end_date) == expected_entries


if __name__ == '__main__':
    unittest.main()
