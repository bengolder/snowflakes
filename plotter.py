import svgwrite
import uuid
from shapely.geometry import Polygon
from shapely.affinity import scale
from chiplotle import (
    hpgl,
    instantiate_plotters
    )


def px(*args):
    return [str(item) + "px" for item in args]


class Drawing:

    def __init__(self, *geoms):
        self.geoms = list(geoms)
        self.get_bounds()
        self.default_preview_filepath = "previews/preview.svg"
        self.plotter = None

    def get_bounds(self):
        self.bounds_poly = Polygon([
            (-11640, -8640),
            (-11640, 8640),
            (10720, 8640),
            (10720, -8640),
            (-11640, -8640),
            ])
        self.bounds = self.bounds_poly.bounds
        self.width = 11640 + 10720
        self.height = 8640 * 2

    def plot(self, geom=None):
        if not self.plotter:
            plotters = instantiate_plotters()
            self.plotter = plotters[0]
        if geom:
            self.add(geom)
        for geom in self.geoms:
            self.plot_geom(geom)

    def add(self, geom):
        self.geoms.append(geom)

    def plot_geom(self, geom):
        if hasattr(geom, 'coords'):
            # assume it is a linear ring or linestring
            self.plot_coords([coord for coord in geom.coords])
        elif hasattr(geom, 'exterior'):
            # assume it has a Polygon-like interface
            self.plot_geom(geom.exterior)
            for ring in geom.interiors:
                self.plot_geom(ring)
        elif hasattr(geom, 'geoms'):
            # assume this is a collection of objects
            for geom in geom.geoms:
                self.plot_geom(geom)
        else:
            raise NotImplementedError(
                "I don't know how to plot {}".format(type(geom)))

    def start_svg(self):
        preview_margin = 100
        screen_height = 600
        svg_width = self.width + (preview_margin * 2)
        svg_height = self.height + (preview_margin * 2)
        screen_width = (svg_width / float(svg_height)) * screen_height
        self.svg = svgwrite.Drawing(
            filename=self.default_preview_filepath,
            size=px(screen_width, screen_height),
            style="background-color: #ccc"
            )
        self.svg.viewbox(
            minx=self.bounds[0] - preview_margin,
            miny=self.bounds[1] - preview_margin,
            width=svg_width,
            height=svg_height,
            )
        self.plotter_geom_group = self.svg.g(
            transform="scale(1, -1)"
            )

    def preview(self, geom=None, filepath=None):
        self.start_svg()
        self.add_bounds_preview()
        if geom:
            self.add(geom)
        for geom in self.geoms:
            self.preview_geom(geom)
        self.svg.save()
        if not filepath:
            filepath = "previews/plot-preview-" + uuid.uuid4().hex + ".svg"
        self.svg.add(self.plotter_geom_group)
        self.svg.saveas(filepath)

    def preview_geom(self, geom, **kwargs):
        if hasattr(geom, 'xy'):
            # assume it is a linear ring or linestring
            self.plotter_geom_group.add(self.svg.polyline(
                points=geom.coords,
                stroke_width="5",
                fill="none",
                stroke="black",)
            )
        elif hasattr(geom, 'exterior'):
            # assume it has a Polygon-like interface
            self.preview_geom(geom.exterior, **kwargs)
            for ring in geom.interiors:
                self.preview_geom(ring, **kwargs)
        elif hasattr(geom, 'geoms'):
            # assume this is a collection of objects
            for geom in geom.geoms:
                self.preview_geom(geom, **kwargs)
        else:
            raise NotImplementedError(
                "I don't know how to preview {}".format(type(geom)))

    def add_bounds_preview(self):
        self.svg.add(self.svg.rect(
            insert=(self.bounds[0], self.bounds[1]),
            size=(self.width, self.height),
            fill="white",
            ))

    def plot_coords(self, coords):
        start = hpgl.PU([coords[0]])
        self.plotter.write(start)
        threshold = 300
        while len(coords) > threshold:
            command = hpgl.PD(coords[:threshold])
            self.plotter.write(command)
            coords = coords[threshold:]
        command = hpgl.PD(coords)
        self.plotter.write(command)
        end = hpgl.PU([coords[-1]])
        self.plotter.write(end)

    def scale_to_fit(self, geom):
        return scale(
            geom,
            xfact=self.scale_ratio,
            yfact=self.scale_ratio,
            origin=(0.0, 0.0),
            )
