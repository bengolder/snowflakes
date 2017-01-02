from plotter import Drawing
from shapely.geometry import (
    Point, MultiLineString, GeometryCollection
    )
from shapely.affinity import scale, rotate, translate
from shapely.ops import cascaded_union
import random
from common_shapes import hexagon as make_hexagon


class Seeder:

    def __init__(self, start_seed=117):
        self.used_seeds = []
        self.current = start_seed

    def new_seed(self):
        new = int(self.current * 1.137)
        self.used_seeds.append(new)
        self.current = new
        return new


class SnowFlake:

    def __init__(self, seed, center=None, rotation=0):
        self.seed = seed
        if not center:
            center = Point(0, 0)
        self.center = center
        self.radius = 5.0
        self.rotation = rotation
        self.shank_width = .35
        self.geom = self.make_layers()

    def make_layers(self):
        random.seed(self.seed)
        base_layer = self.make_layer(5, 0.5, 1.5)
        top_layer = self.make_layer(20, .05, .50)
        snowflake = GeometryCollection([base_layer, top_layer])
        if self.rotation:
            snowflake = rotate(snowflake, self.rotation, origin=Point(0, 0))
        return translate(
            snowflake,
            xoff=self.center.x,
            yoff=self.center.y)

    def make_layer(self, num_hexagons, rmin, rmax):
        hexagons = make_hexagons(
            num_hexagons, self.shank_width, self.radius, rmin, rmax)
        shank = make_shank(hexagons)
        full_layer = twist_shank(shank, Point(0, 0))
        return full_layer


def points_to_coord_tuples(points):
    return [(p.x, p.y) for p in points]


def make_hexagons(num_hexagons, xmax, ymax, rmin, rmax):
    hexagons = []
    rdiff = rmax - rmin
    for x in range(num_hexagons):
        center_x = random.random() * xmax
        center_y = random.random() * ymax
        radius = (random.random() * rdiff) + rmin
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


def cross(center, width=0.5):
    x0 = center.x - (width * 0.5)
    x1 = center.x + (width * 0.5)
    y0 = center.y - (width * 0.5)
    y1 = center.y + (width * 0.5)
    return MultiLineString([
        ((x0, center.y), (x1, center.y)),
        ((center.x, y1), (center.x, y0))
    ])


def run(starter=301):
    drawing = Drawing()
    drawing.add_paper(24, 18)
    card_width = 5
    card_height = 7
    cards_x = 3
    cards_y = 3
    card_x_offset = -11
    card_y_offset = -7.5
    for ix in range(cards_x + 1):
        for iy in range(cards_y + 1):
            cut_mark = cross(Point(
                (ix * card_height) + card_x_offset,
                (iy * card_width) + card_y_offset
                ))
            drawing.add(cut_mark)

    # seed_ints = [
    #     11, 19, 21, 23, 26, 28, 36, 38, 40, 41, 42, 44, 45, 49, 51,
    #     52, 54, 55, 56, 57, 58]
    # seed_ints.extend([
    #     seed * 2 for seed in seed_ints])
    # seed_ints.extend([
    #     seed * 2 for seed in seed_ints])
    scalar = 0.075 * 1.75
    spacing_seed = 9182
    random.seed(spacing_seed)
    angle_choices = [0, 15, 30, 45]
    position_choices = [
        Point(5.2, 1.8),
        Point(2.8, 4.1),
        Point(1.5, 1.2),
        Point(3.6, 2.4),
        Point(5.4, 3.9)
    ]
    snowflake_seeder = Seeder(starter)
    # angles = [random.choice(angle_choices) for i in range(len(seed_ints))]
    snowflakes = []
    for i in range(47):
        angle = random.choice(angle_choices)
        seed_int = snowflake_seeder.new_seed()
        snowflake = SnowFlake(seed_int, rotation=angle).geom
        snowflake = scale(
            snowflake, scalar, scalar, origin='centroid')
        snowflakes.append(snowflake)

    for i in range(3):
        for j in range(3):
            card_x = card_x_offset + i * 7
            card_y = card_y_offset + j * 5
            card_origin = Point(card_x, card_y)
            # pop off three snowflakes from list of snowflakes
            for k, position in enumerate(position_choices):
                flake = snowflakes.pop(0)
                flake_x = card_origin.x + position.x
                flake_y = card_origin.y + position.y
                moved_flake = translate(flake, xoff=flake_x, yoff=flake_y)
                if k > 2:
                    moved_flake = scale(
                         moved_flake, 2.2, 2.2, origin="centroid")
                drawing.add(moved_flake)
    drawing.preview(filepath='previews/preview-seed-' + str(starter) + '.svg')
    drawing.plot()

if __name__ == '__main__':
    # for i in range(312, 322):
        run(319)
