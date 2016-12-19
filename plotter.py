from matplotlib import pyplot
from shapely.geometry import Polygon, LineString
from shapely.affinity import scale, rotate
from chiplotle import (
    hpgl,
    instantiate_plotters
    )


class Drawing:

    def __init__(self, geoms=None):
        self.geoms = geoms or []
        self.get_bounds()
        self.fig = pyplot.figure(1, figsize=(5, 5), dpi=300)
        pyplot.axis([-11640, 10720, -11640, 10720])
        self.subplot = self.fig.add_subplot(111)
        self.subplot.set_title('Plotter Preview')
        self.default_style = dict(
            color='#0000ff', alpha=0.6,
            linewidth=0.3, solid_capstyle='round')
        self.add_bounds_preview()
        self.plotter = None
        # self.scale_ratio = self.height / 1000
        self.scale_ratio = 2.8
        # self.scale_ratio = 6

    def plot(self, geom=None):
        if not self.plotter:
            plotters = instantiate_plotters()
            self.plotter = plotters[0]
        if geom:
            self.add(geom)
        for geom in self.geoms:
            self.plot_geom(geom)

    def add(self, geom):
        self.geoms.append(self.scale_to_fit(geom))

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

    def preview(self, geom=None, filename="plot.png"):
        if geom:
            self.add(geom)
        self.add_bounds_preview()
        for geom in self.geoms:
            self.preview_geom(geom)
        pyplot.savefig(filename, dpi=300)

    def preview_geom(self, geom, **kwargs):
        if hasattr(geom, 'xy'):
            # assume it is a linear ring or linestring
            x, y = geom.xy
            style = self.default_style.copy()
            style.update(kwargs)
            self.subplot.plot(x, y, **style)
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

    def add_bounds_preview(self):
        self.preview_geom(
            self.bounds_poly, color="#AAAAAA",
            linewidth=2)

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
