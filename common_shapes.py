from shapely.geometry import Point, Polygon
from shapely.affinity import rotate


def regular_polygon(center, radius, sides=3):
    angle = 360 / sides
    first_point = Point(center.x + radius, center.y)
    coords = [first_point.coords[0]]
    for side in range(sides):
        next_point = rotate(first_point, angle * side, origin=center)
        coords.append(next_point.coords[0])
    return Polygon(coords)


def heptagon(center, radius):
    return regular_polygon(center, radius, 6)


def hexagon(center, radius):
    return regular_polygon(center, radius, 6)


def pentagon(center, radius):
    return regular_polygon(center, radius, 7)


def square(center, radius):
    return regular_polygon(center, radius, 4)


def triangle(center, radius):
    return regular_polygon(center, radius, 3)

if __name__ == '__main__':
    from plotter import Drawing
    drawing = Drawing()
    drawing.add(hexagon(Point(-1200, 0), 600))
    drawing.add(regular_polygon(Point(200, 0), 600, 7))
    drawing.preview(filepath="previews/common_shapes.png")
