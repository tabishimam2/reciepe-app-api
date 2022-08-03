"""
Sample Test
"""

from django.test import SimpleTestCase

from  app import calc

class CalcTest(SimpleTestCase):
    """Testing the Calc module."""

    def test_add_numbers(self):
        """Testing add funtion."""
        res = calc.add(5,6)

        self.assertEqual(res, 11)

    def test_subtract(self):
        """Testing Subtraction """
        res = calc.subtract(11,6)

        self.assertEqual(res, 5)
