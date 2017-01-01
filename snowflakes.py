from plotter import Drawing
from shapely.geometry import Polygon, Point, GeometryCollection
from shapely.affinity import scale, rotate, translate
from shapely.ops import cascaded_union
from random import randint, seed as set_seed
from math import floor

set_seed(19)
# 5, 6, 8, 20
# printed: 11, 19, 21, 23, 26, 28, 36, 38, 40, 41, 42, 44, 45, 49, 51, 52, 54, 55, 56, 57, 58


def points_to_coord_tuples(points):
    return [(p.x, p.y) for p in points]


def make_hexagon(center, radius):
    # center is a Shapely point
    coords = [Point(center.x + radius, center.y)]
    point = coords[0]
    for x in range(6):
        new_point = rotate(point, 60 * x, origin=center)
        coords.append(new_point)
    coord_tuples = points_to_coord_tuples(coords)
    hexagon = Polygon(coord_tuples)
    return hexagon


def make_hexagons(num_hexagons, xmin, xmax, ymin, ymax, rmin, rmax):
    hexagons = []
    for x in range(num_hexagons):
        center_x = randint(xmin, xmax)
        center_y = randint(ymin, ymax)
        radius = randint(rmin, rmax)
        hexagons.append(
            make_hexagon(
                Point(center_x, center_y),
                radius
            )
        )
    return hexagons


def make_shank(hexagons):
    union = cascaded_union(hexagons)
    union_reflection = scale(union, -1.0, 1.0, origin=Point(0, 0))
    return cascaded_union([union, union_reflection])


def twist_shank(shank, center):
    shankles = [shank]
    for x in range(1, 6):
        shanklet = rotate(shank, 60 * x, origin=center)
        shankles.append(shanklet)
    return cascaded_union(shankles)


def make_snowflake_layer(num_hexagons, r_min, r_max):
    hexagons = make_hexagons(num_hexagons, 0, 35, 0, 500, r_min, r_max)
    shank = make_shank(hexagons)
    full_snowflake = twist_shank(shank, Point(0, 0))
    return full_snowflake


def make_snowflake(seed, origin, rotation=0):
    """origin is assumed to be a shapely.geometry.Point
    rotation is in degrees
    """
    set_seed(seed)
    base_layer = make_snowflake_layer(5, 50, 150)
    top_layer = make_snowflake_layer(20, 5, 50)
    snowflake = GeometryCollection([base_layer, top_layer])
    return rotate(
        translate(snowflake, xoff=origin.x, yoff=origin.y),
        rotation, origin=origin)


def run():
    drawing = Drawing()
    seed_ints = [
        11, 19, 21, 23, 26, 28, 36, 38, 40, 41, 42, 44, 45, 49, 51,
        52, 54, 55, 56, 57, 58]
    x_init = -3200
    y_init = 1200
    x_offset = 1400
    y_offset = -1400
    snowflakes_per_row = 5
    for i, seed_int in enumerate(seed_ints):
        row = floor(i/snowflakes_per_row)
        flake_x = x_init + (i % snowflakes_per_row) * x_offset
        flake_y = y_init + row * y_offset
        flake_origin = Point(flake_x, flake_y)
        snowflake = make_snowflake(seed_int, flake_origin)
        if i < 15:
            drawing.add(snowflake)
    drawing.preview()
    # drawing.plot()

if __name__ == '__main__':
    run()
