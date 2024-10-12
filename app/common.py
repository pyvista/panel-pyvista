from typing import Any
import panel as pn
from pyvista.plotting import Plotter
from matplotlib import colormaps


# 'client' : Export/serialize the scene graph to be rendered with VTK.js
# 'server': Render remotely and stream the resulting VTK images back to the client
DEFAULT_BACKEND = "client"

# Generate list of colormap names
CMAPS = [str(key) for key in colormaps.keys()]


class GlobalStateMixin:
    """Mixin to propagate the app instance and state to all components"""

    @property
    def app(self):
        return pn.state.cache["app"]


def show_panel(
    plotter: Plotter, jupyter_backend: str = DEFAULT_BACKEND, **kwargs: Any
) -> pn.pane.HTML:
    def panel_handler(viewer, src, **_kwargs):
        html = f'<iframe src="{src}" class="pyvista" style="width: 100%; height: 100%;"></iframe>'
        return pn.pane.HTML(html, sizing_mode="stretch_both")

    # enable proxying
    kwargs.setdefault("jupyter_kwargs", {})
    kwargs["jupyter_kwargs"]["handler"] = panel_handler
    kwargs["jupyter_kwargs"]["server_proxy_enabled"] = True
    kwargs["jupyter_kwargs"]["server_proxy_prefix"] = "/proxy/"

    # Always return the viewer to access the Panel object
    kwargs["return_viewer"] = True

    return plotter.show(
        jupyter_backend=jupyter_backend,
        **kwargs,
    )
