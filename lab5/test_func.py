# модульные тесты для функции get_triangle_type с использованием unittest

import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides


class TestGetTriangleType(unittest.TestCase):
    """тесты для функции get_triangle_type"""
    
    # позитивные тесты
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")
        self.assertEqual(get_triangle_type(5.5, 5.5, 5.5), "equilateral")
    
    def test_isosceles(self):
        self.assertEqual(get_triangle_type(5, 5, 3), "isosceles")
        self.assertEqual(get_triangle_type(5, 3, 5), "isosceles")
        self.assertEqual(get_triangle_type(3, 5, 5), "isosceles")
    
    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")
        self.assertEqual(get_triangle_type(7, 8, 9), "nonequilateral")
    
    # негативные тесты
    def test_negative_side(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 2, 3)
    
    def test_zero_side(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 2, 3)
    
    def test_triangle_inequality(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 10)
    
    def test_sum_equals_third(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)
    
    def test_non_numeric(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type("a", 2, 3)
    
    def test_none_argument(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(None, 2, 3)


if __name__ == "__main__":
    unittest.main()