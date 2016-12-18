from plotter import Plotter
from shapely.geometry import Polygon, Point
from shapely.affinity import scale, rotate
from shapely.ops import cascaded_union
from random import randint, seed

seed(11)
#5, 6, 8,  

def points_to_coord_tuples(points):
    return [(p.x, p.y) for p in points]

def make_hexagon(center, radius):
    #center is a Shapely point
    coords = [Point(center.x + radius, center.y)]
    point = coords[0]
    for x in range(6):
        new_point = rotate(point,60 * x, origin=center)
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
    union_reflection = scale(union, -1.0, 1.0, origin=Point(0,0))
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

def add_geometry_to_preview(drawing, geometry, **kwargs):
    if isinstance(geometry, Polygon):
        drawing.add_polygon(geometry, **kwargs)
    else:
        for poly in geometry.geoms:
            drawing.add_polygon(poly, **kwargs)

def draw_snowflake_layer(drawing, num_hexagons, r_min, r_max, **kwargs):
    snowflake_layer = make_snowflake_layer(num_hexagons, r_min, r_max)
    add_geometry_to_preview(drawing, snowflake_layer, **kwargs)

def run():
    drawing = Plotter(plot=False)
    draw_snowflake_layer(drawing, 5, 50, 150, color="#FF0000")
    #draw_snowflake_layer(drawing, 50, 5, 50)
    draw_snowflake_layer(drawing, 20, 5, 50, color="#0000FF")
    drawing.save_preview()
    
if __name__ == '__main__':
    run()