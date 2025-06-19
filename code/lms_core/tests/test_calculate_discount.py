from django.test import TestCase
from lms_core.utils import calculate_discount 
class UtilsTest(TestCase):

    def test_calculate_discount(self):
        self.assertEqual(calculate_discount(100, 10), 90)
        self.assertEqual(calculate_discount(200, 50), 100)

    def test_calculate_discount_invalid(self):
        with self.assertRaises(ValueError):
            calculate_discount(100, -10)
        with self.assertRaises(ValueError):
            calculate_discount(100, 110)