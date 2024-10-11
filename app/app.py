import os
import panel as pn
from pyvista_panel import PyVistaPlotter
from fea_panel import FeaPlotter
from jsp_proxy import ProxyHandler
from pyvista.trame.jupyter import elegantly_launch

from constants import PYVISTA_PORT

# start trame
elegantly_launch(port=PYVISTA_PORT, host="localhost")


def App():
    # this will launch an individual plotter for each user
    pv_viewer = PyVistaPlotter()
    fea_viewer = FeaPlotter()
    tabs = pn.Tabs(
        ("PyVista", pv_viewer),
        ("FEA Viewer", fea_viewer),
    )
    return tabs


server = pn.serve(
    {
        "/": App,
    },
    port=os.environ.get("APP_PORT", 8080),
    show=False,
    websocket_origin=["*"],
    start=False,
    title="PyVista Panel Demo",
)
server._tornado.add_handlers(r".*", [("/proxy/.*", ProxyHandler)])
server.start()
server.io_loop.start()
