import panel as pn
import pyvista as pv
from pyvista.plotting import Plotter
from pyvista.trame.jupyter import elegantly_launch
from pyvista import demos as pv_demos

from common import GlobalStateMixin

elegantly_launch(port=5090)
# elegantly_launch(port=5090, wslink_backend="tornado")  # doesn't work

pv.set_plot_theme("document")
pv.global_theme.show_scalar_bar = False


def show_panel(
    plotter: Plotter, jupyter_backend: str = "server", **kwargs
) -> pn.pane.HTML:
    def panel_handler(viewer, src, **_kwargs):
        html = f'<iframe src="{src}" class="pyvista" style="width: 100%; height: 100%;"></iframe>'
        return pn.pane.HTML(html, sizing_mode="stretch_both")

    kwargs.setdefault("jupyter_kwargs", {})
    kwargs["jupyter_kwargs"]["handler"] = panel_handler

    # Always return the viewer to access the Panel object
    kwargs["return_viewer"] = True

    return plotter.show(
        jupyter_backend=jupyter_backend,
        **kwargs,
    )


class PyVistaPlotter(GlobalStateMixin, pn.viewable.Viewer):
    def __init__(self, jupyter_backend: str = "server", **kwargs):
        super().__init__(**kwargs)
        self._plotter = Plotter(off_screen=True, notebook=True)
        self._plotter.add_axes()
        self._plotter_pane = show_panel(self.plotter, jupyter_backend=jupyter_backend)
        self._plotter.camera_set = False

        pl = pv_demos.plot_logo(just_return_plotter=True)
        for actor in pl.actors.values():
            self._plotter.add_actor(actor)

        self._plotter.camera_position = "xy"

    @property
    def plotter(self):
        return self._plotter

    def __panel__(self):
        return self._plotter_pane

    def add_mesh(self, mesh, **kwargs):
        self.plotter.add_mesh(mesh, **kwargs)
        self.plotter.update()
