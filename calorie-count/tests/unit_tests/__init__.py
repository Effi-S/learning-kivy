import unittest
from tests.unit_tests.test_DB import test_food_db, test_meal_entry_db
from tests.unit_tests.test_utils import test_utils, test_xlsx

if __name__ == '__main__':
    modules = (test_food_db, test_meal_entry_db, test_utils, test_xlsx)
    loaders = map(unittest.defaultTestLoader.loadTestsFromModule, modules)
    suite = unittest.TestSuite(loaders)
    unittest.TextTestRunner().run(suite)
