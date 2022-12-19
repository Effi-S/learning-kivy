"""Here we test the MealEntryDB methods.

Please note that adding a test requires the patch for __enter__ for FoodDB to return our test db 'self.fdb'.
This is because of  "separation of concerns", MealEntry object calls FoodDB.__enter__ .
Though a bit hacky, This patch seems simpler than injecting the test FoodDB
to MealEntryDB who injects it to MealEntry Objects.

"""
import unittest
from unittest.mock import patch

from src.DB.food_db import FoodDB, Food
from src.DB.meal_entry_db import MealEntry, MealEntryDB
from src.utils import config


class TestFoodDB(unittest.TestCase):

    def setUp(self):
        # Create a new instance of FoodDB for each test method
        config.set_db_path_test()
        self.fdb = FoodDB()  # So table will exist as well
        super().setUp()

    def tearDown(self) -> None:
        self.fdb.conn.close()

    @patch('src.DB.food_db.FoodDB.__enter__')
    def test_add_meal_entry(self, mock: unittest.mock.Mock):
        mock.return_value = self.fdb
        self.fdb.path = 'Hello There!'
        self.fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
        # Test adding a new meal entry
        entry = MealEntry(name="apple", date="2022-12-15", portion=100)
        print(entry)
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(entry)

            # Check that the entry was added to the database
            ret = mdb.get_entries_between_dates("2022-12-14", "2022-12-16")
            self.assertEqual(len(ret), 1)

    @patch('src.DB.food_db.FoodDB.__enter__')
    def test_delete_entry(self, mock: unittest.mock.Mock):
        mock.return_value = self.fdb
        self.fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
        # Test deleting a meal entry
        entry = MealEntry(name="apple", date="2022-12-15", portion=100)
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(entry)
            self.assertEqual(len(mdb.get_entries_between_dates("2022-12-15", "2022-12-15")), 1)
            mdb.delete_entry(entry.id)
            # Check that the entry was deleted from the database
            self.assertEqual(len(mdb.get_entries_between_dates("2022-12-15", "2022-12-15")), 0)

    @patch('src.DB.food_db.FoodDB.__enter__')
    def test_get_first_last_dates(self, mock: unittest.mock.Mock):
        mock.return_value = self.fdb
        self.fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
        self.fdb.add_food(Food('banana', 100, 0.5, 0.2, 10, 4, 0, 86))
        # Test getting the first and last dates in the database
        entry1 = MealEntry(name="apple", date="2022-12-14", portion=100)
        entry2 = MealEntry(name="banana", date="2022-12-16", portion=100)
        with MealEntryDB() as mdb:
            mdb.add_meal_entry(entry1)
            mdb.add_meal_entry(entry2)
            first_date, last_date = mdb.get_first_last_dates()
            # Check that the first and last dates in the database are as expected
            self.assertEqual(first_date.isoformat(), "2022-12-14")
            self.assertEqual(last_date.isoformat(), "2022-12-16")

    @patch('src.DB.food_db.FoodDB.__enter__')
    def test_get_entries_between_dates(self, mock: unittest.mock.Mock):
        mock.return_value = self.fdb
        # Create a MealEntryDB instance and add some MealEntry objects to it
        self.fdb.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))
        self.fdb.add_food(Food('banana', 100, 0.5, 0.2, 10, 4, 0, 86))
        self.fdb.add_food(Food('orange', 100, 0.5, 0.2, 10, 4, 0, 86))
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
            assert mdb.get_entries_between_dates(start_date, end_date) == expected_entries


if __name__ == '__main__':
    unittest.main()
