import unittest

from calorie_count.src.utils.utils import sort_by_similarity


class TestSortBySimilarity(unittest.TestCase):
    def test_empty_list(self):
        self.assertEqual(sort_by_similarity([], 'hello'), [])

    def test_unsorted_list(self):
        self.assertEqual(next(iter(sort_by_similarity(['world', 'bar', 'hello', 'foo'], 'hello'))), 'hello')

    def test_case_insensitivity(self):
        self.assertEqual(next(iter(sort_by_similarity(['Hello', 'world', 'foo', 'bar'], 'hello'))), 'Hello')

    def test_tuple(self):
        tup = ('world', 'Johnny', 'hello', 'foo')
        self.assertEqual(next(iter(sort_by_similarity(tup, 'john'))), 'Johnny')

# TODO make mock app for testing this TextField and for components
# class TestRTLMDTextField(unittest.TestCase):
#
#     @patch.object(MDTextField, 'insert_text')
#     def test_insert_rtl_text(self, mock_insert_text):
#         text_field = RTLMDTextField()
#         text_field.insert_text('ش')
#         mock_insert_text.assert_called_once_with('ش', from_undo=False)
#         self.assertEqual(text_field.text, 'ش')


if __name__ == '__main__':
    unittest.main()
