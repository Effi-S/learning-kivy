import atexit
import os
import unittest
import uuid

from src.DB.food_db import FoodDB, Food
from src.DB.meal_entry_db import MealEntryDB
from src.utils import config


class TestFoodDB(unittest.TestCase):
    def setUp(self):
        # Create a new instance of FoodDB for each test method
        config.set_db_path_test()
        self.db = FoodDB()
        with MealEntryDB():  # So table will exist as well
            pass
        super().setUpClass()

    def tearDown(self) -> None:
        self.db.conn.close()

    def test_remove(self):
        # Add food to the database
        self.db.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))

        # Check that the food was added successfully
        self.assertIn('apple', self.db.get_all_food_names())

        # Remove the food from the database
        self.db.remove(['apple'])

        # Check that the food was removed successfully
        self.assertNotIn('apple', self.db.get_all_food_names())

    def test_add_food(self):
        # Create a new food
        food = Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86)

        # Add the food to the database
        self.db.add_food(food)

        # Check that the food was added successfully
        self.assertIn('apple', self.db.get_all_food_names())

    def test_get_food_by_id(self):
        # Add a food to the database
        self.db.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))

        # Get the food by id
        food = self.db.get_food_by_id('apple')

        # Check that the returned food has the expected properties
        self.assertEqual(food.name, 'apple')
        self.assertEqual(food.portion, 100)
        self.assertEqual(food.proteins, 0.5)
        self.assertEqual(food.fats, 0.2)
        self.assertEqual(food.carbs, 10)
        self.assertEqual(food.sugar, 4)
        self.assertEqual(food.sodium, 0)
        self.assertEqual(food.water, 86)

    def test_get_food_by_name(self):
        # Add Food to the database
        self.db.add_food(Food('apple', 100, 0.5, 0.2, 10, 4, 0, 86))

        # Get the food by name
        food = self.db.get_food_by_name('apple')

        # Check that the returned food has the expected properties
        self.assertEqual(food.name, 'apple')
        self.assertEqual(food.portion, 100)
        self.assertEqual(food.proteins, 0.5)
        self.assertEqual(food.fats, 0.2)
        self.assertEqual(food.carbs, 10)
        self.assertEqual(food.sugar, 4)
        self.assertEqual(food.sodium, 0)
        self.assertEqual(food.water, 86)


if __name__ == '__main__':
    unittest.main()
