from shapely.geometry import MultiLineString
from shapely.affinity import rotate


def hatch(geom, offset, angle=45):
    minx, miny, maxx, maxy = geom.bounds
    midx = (maxx + minx) / 2
    midy = (maxy + miny) / 2
    length = (
        max((maxx - minx, maxy - miny)) * 2
        )
    bottom = midy - (length / 2)
    top = midy + (length / 2)
    left = midx - (length / 2)
    right = midx + (length / 2)
    lines = []
    x = left
    while x <= right:
        lines.append(
            ((x, bottom), (x, top))
        )
        x += offset
    hatch_lines = MultiLineString(lines)
    if angle != 0:
        hatch_lines = rotate(hatch_lines, angle, origin=(midx, midy))
    return geom.intersection(hatch_lines)


if __name__ == '__main__':
    from common_shapes import regular_polygon
    from shapely.geometry import Point
    from plotter import Drawing
    geom = regular_polygon(Point(0, 0), 8000, sides=50)
    hatches = hatch(geom, 150, 42)
    drawing = Drawing(hatches)
    drawing.preview(filepath="previews/hatches.png")
