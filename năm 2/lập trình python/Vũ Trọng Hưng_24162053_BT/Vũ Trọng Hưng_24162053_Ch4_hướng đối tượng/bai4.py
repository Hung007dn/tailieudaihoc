#Vũ Trọng Hưng 24162053
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise TypeError("Chỉ cộng được với Point")

    def __str__(self):
        return f"({self.x}, {self.y})"
points = [
    Point(1, 2),
    Point(3, 4),
    Point(5, 6)
]

result = Point(0, 0)
for p in points:
    result = result + p   # đa hình qua operator +

print("Tổng các điểm:", result)
