# класс Triangle с методами для работы с треугольником


class IncorrectTriangleSides(Exception):
    """исключение для некорректных сторон треугольника"""
    pass


class Triangle:
    """класс, описывающий треугольник по трём сторонам"""
    
    def __init__(self, a, b, c):
        """
        конструктор треугольника
        
        аргументы:
            a, b, c: длины сторон треугольника
        
        выбрасывает:
            IncorrectTriangleSides: если стороны некорректны
        """
        # валидация входных данных
        if not all(isinstance(side, (int, float)) for side in [a, b, c]):
            raise IncorrectTriangleSides("все стороны должны быть числами")
        
        if any(side <= 0 for side in [a, b, c]):
            raise IncorrectTriangleSides("стороны должны быть положительными")
        
        sides = sorted([a, b, c])
        if sides[0] + sides[1] <= sides[2]:
            raise IncorrectTriangleSides("не выполняется неравенство треугольника")
        
        self.a = a
        self.b = b
        self.c = c
    
    def triangle_type(self):
        """возвращает тип треугольника: equilateral, isosceles, nonequilateral"""
        if self.a == self.b == self.c:
            return "equilateral"
        elif self.a == self.b or self.b == self.c or self.a == self.c:
            return "isosceles"
        else:
            return "nonequilateral"
    
    def perimeter(self):
        """возвращает периметр треугольника"""
        return self.a + self.b + self.c