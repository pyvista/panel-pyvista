import panel as pn
import pyvista as pv
from pyvista import demos as pv_demos

from common import GlobalStateMixin

pn.extension("vtk")

pv.set_plot_theme("document")
pv.global_theme.show_scalar_bar = False


plotter = pv.Plotter()  # we define a pyvista plotter
plotter.background_color = (0.1, 0.2, 0.4)
# we create a `VTK` panel around the render window
pn.panel(plotter.ren_win, width=500, height=500)


class PyVistaPlotter(GlobalStateMixin, pn.viewable.Viewer):
    def __init__(self):
        self._plotter = pv.Plotter()  # we define a pyvista plotter

        pl = pv_demos.plot_logo(just_return_plotter=True)
        for actor in pl.actors.values():
            self._plotter.add_actor(actor)

        self._plotter.camera_position = "xy"

        # Create a `VTK` panel around the render window
        self._vtk_panel = pn.panel(self._plotter.ren_win, width=1000, height=500)

    @property
    def plotter(self):
        return self._plotter

    def __panel__(self):
        return self._vtk_panel

    def add_mesh(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)
        self.plotter.update()
