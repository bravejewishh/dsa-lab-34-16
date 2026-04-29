# функция определения типа треугольника по длинам сторон


class IncorrectTriangleSides(Exception):
    """исключение для некорректных сторон треугольника"""
    pass


def get_triangle_type(a, b, c):
    """
    определяет тип треугольника по трём сторонам
    
    аргументы:
        a, b, c: числовые значения длин сторон
    
    возвращает:
        str: 'equilateral', 'isosceles' или 'nonequilateral'
    
    выбрасывает:
        IncorrectTriangleSides: если стороны некорректны
    """
    # проверка на числовые значения
    if not all(isinstance(side, (int, float)) for side in [a, b, c]):
        raise IncorrectTriangleSides("все стороны должны быть числами")
    
    # проверка на положительные значения
    if any(side <= 0 for side in [a, b, c]):
        raise IncorrectTriangleSides("стороны треугольника должны быть положительными")
    
    # проверка неравенства треугольника
    sides = sorted([a, b, c])
    if sides[0] + sides[1] <= sides[2]:
        raise IncorrectTriangleSides("не выполняется неравенство треугольника")
    
    # определение типа треугольника
    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"