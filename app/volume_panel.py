from typing import Any

import panel as pn
from pyvista import examples
from pyvista.plotting import Plotter
from param.parameterized import Event

from common import show_panel, CMAPS

pn.extension("floatpanel")

carotid = examples.download_carotid()

# for testing
# plotter = Plotter()
# actor = plotter.add_volume(carotid)
# actor.mapper.lookup_table.apply_opacity([1, 1])
# # actor.mapper.lookup_table.cmap
# # actor.mapper.update()
# plotter.volume.prop.apply_lookup_table(actor.mapper.lookup_table)
# plotter.show()

OPACITY_OPTIONS = [
    "linear",
    "linear_r",
    "geom",
    "geom_r",
    "sigmoid",
    "sigmoid_1",
    "sigmoid_2",
    "sigmoid_3",
    "sigmoid_4",
    "sigmoid_5",
    "sigmoid_6",
    "sigmoid_7",
    "sigmoid_8",
    "sigmoid_9",
    "sigmoid_10",
    "sigmoid_15",
    "sigmoid_20",
    "foreground",
]


class VolumePlotter(pn.viewable.Viewer):
    def __init__(self, jupyter_backend: str = "client", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._plotter = Plotter(off_screen=True, notebook=True)
        self._plotter.add_axes()  # type:ignore
        self._plotter_pane = show_panel(self._plotter, jupyter_backend=jupyter_backend)

        # add the dataset
        self._actor = self._plotter.add_volume(carotid)
        self._plotter.view_isometric()  # type: ignore

        self._opacity_select = pn.widgets.Select(
            name="Opacity", options=OPACITY_OPTIONS, value="linear"
        )
        self._opacity_select.param.watch(self._update_opacity, "value")

        self._colormap_select = pn.widgets.Select(
            name="Colormap", options=CMAPS, value="viridis"
        )
        self._colormap_select.param.watch(self._update_colormap, "value")

        self._floatpanel = pn.layout.FloatPanel(
            self._opacity_select,
            self._colormap_select,
            name="Plot Settings",
            margin=20,
            contained=True,
            offsetx=13,
            offsety=140,
        )

    def _update_opacity(self, event: Event) -> None:
        """Apply the new opacity to the lookup table."""
        # we have to separately apply the colormap back to the volume property (bug?)
        self._actor.mapper.lookup_table.apply_opacity(event.new)
        self._actor.prop.apply_lookup_table(self._actor.mapper.lookup_table)
        self._plotter.render()

    def _update_colormap(self, event: Event) -> None:
        # we have to separately apply the colormap back to the volume property (bug?)
        self._actor.mapper.lookup_table.cmap = event.new
        self._actor.prop.apply_lookup_table(self._actor.mapper.lookup_table)
        self._plotter.render()

    def __panel__(self):
        return pn.Column(
            self._floatpanel,
            self._plotter_pane,
        )
