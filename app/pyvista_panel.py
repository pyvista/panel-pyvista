import panel as pn
import pyvista as pv
from pyvista import demos as pv_demos

from common import GlobalStateMixin

pn.extension("vtk")

pv.set_plot_theme("document")
pv.global_theme.show_scalar_bar = False


class PyVistaPlotter(GlobalStateMixin, pn.viewable.Viewer):
    def __init__(self):
        self._plotter = pv.Plotter()  # we define a pyvista plotter

        pl = pv_demos.plot_logo(just_return_plotter=True)
        for actor in pl.actors.values():
            actor.prop.interpolation = 0
            self._plotter.add_actor(actor)

        self._plotter.camera_position = "xy"

        # Create a `VTK` panel around the render window
        self._vtk_panel = pn.panel(
            self._plotter.ren_win, sizing_mode="stretch_both", height=500
        )

    @property
    def plotter(self):
        return self._plotter

    def __panel__(self):
        return self._vtk_panel

    def add_mesh(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)
        self.plotter.update()
