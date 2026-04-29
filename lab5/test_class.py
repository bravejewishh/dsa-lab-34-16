# модульные тесты для класса Triangle с использованием pytest

import pytest
from triangle_class import Triangle, IncorrectTriangleSides


class TestTriangleClass:
    """тесты для класса Triangle"""
    
    # позитивные тесты создания объекта
    def test_create_valid_triangle(self):
        triangle = Triangle(3, 4, 5)
        assert triangle.a == 3
        assert triangle.b == 4
        assert triangle.c == 5
    
    def test_create_with_floats(self):
        triangle = Triangle(2.5, 3.5, 4.0)
        assert triangle.perimeter() == 10.0
    
    # тесты метода triangle_type
    def test_equilateral_type(self):
        triangle = Triangle(5, 5, 5)
        assert triangle.triangle_type() == "equilateral"
    
    def test_isosceles_type(self):
        triangle = Triangle(5, 5, 3)
        assert triangle.triangle_type() == "isosceles"
    
    def test_nonequilateral_type(self):
        triangle = Triangle(3, 4, 5)
        assert triangle.triangle_type() == "nonequilateral"
    
    # тесты метода perimeter
    def test_perimeter_integer(self):
        triangle = Triangle(3, 4, 5)
        assert triangle.perimeter() == 12
    
    def test_perimeter_float(self):
        triangle = Triangle(2.5, 3.5, 4.0)
        assert triangle.perimeter() == 10.0
    
    # негативные тесты создания объекта
    def test_negative_side(self):
        with pytest.raises(IncorrectTriangleSides):
            Triangle(-1, 2, 3)
    
    def test_zero_side(self):
        with pytest.raises(IncorrectTriangleSides):
            Triangle(0, 2, 3)
    
    def test_triangle_inequality_violation(self):
        with pytest.raises(IncorrectTriangleSides):
            Triangle(1, 2, 10)
    
    def test_sum_equals_third(self):
        with pytest.raises(IncorrectTriangleSides):
            Triangle(1, 2, 3)
    
    def test_non_numeric_side(self):
        with pytest.raises(IncorrectTriangleSides):
            Triangle("a", 2, 3)
    
    def test_none_side(self):
        with pytest.raises(IncorrectTriangleSides):
            Triangle(None, 2, 3)