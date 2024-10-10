from typing import Any

import numpy as np
import panel as pn
import pyvista as pv
from pyvista.core.utilities.helpers import generate_plane
from pyvista import examples
from pyvista.plotting import Plotter
from pyvista.trame.jupyter import elegantly_launch
from param.parameterized import Event
from pyvista.core.filters import _get_output
from pyvista.plotting import _vtk

from pyvista.plotting.utilities import (
    add_ids_algorithm,
    algorithm_to_mesh_handler,
    outline_algorithm,
    set_algorithm_input,
)


from constants import PYVISTA_PORT
from common import DEFAULT_BACKEND, show_panel, CMAPS

elegantly_launch(port=PYVISTA_PORT, host="localhost")

# Define stress components
STRESS_TYPES = ["X", "Y", "Z", "XY", "YZ", "XZ"]
DEFAULT_CMAP = "jet"


class FeaPlotter(pn.viewable.Viewer):
    def __init__(self, jupyter_backend: str = DEFAULT_BACKEND, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._plotter = Plotter(off_screen=True, notebook=True)
        self._plotter.add_axes()  # type:ignore
        self._plotter_pane = show_panel(self._plotter, jupyter_backend=jupyter_backend)

        # Load the mesh and fix the cell types (quadratic --> linear)
        mesh = examples.download_notch_stress()
        mesh.cell_connectivity
        celltypes = mesh.celltypes
        fixed_cells = []
        cells = np.split(mesh.cell_connectivity, mesh.offset)[1:-1]
        for idx, cell in enumerate(cells):
            if celltypes[idx] == pv.CellType.HEXAHEDRON:
                fixed_cells.append(np.hstack(([8], cell[:8])))
            elif celltypes[idx] == pv.CellType.WEDGE:
                fixed_cells.append(np.hstack(([6], cell[:6])))

        new_mesh = pv.UnstructuredGrid(np.hstack(fixed_cells), celltypes, mesh.points)
        for ii in range(6):
            new_mesh[f"Nodal Stress-{ii}"] = mesh["Nodal Stress"][:, ii]

        # Add the mesh to the plotter
        self._mesh = new_mesh
        self._xrange = new_mesh.bounds[:2]
        self._clip_callback, self._actor = self.add_mesh_clip_plane(
            new_mesh,
            scalars="Nodal Stress-0",
            cmap=DEFAULT_CMAP,
            ambient=0.15,
            origin=(0.0, 0, 0),
            show_edges=True,
        )
        self._plane_widget = self._plotter.plane_widgets[0]

        self._plane_widget.Off()
        self._plane_widget.DrawPlaneOff()
        self._plane_widget.GetNormalProperty().SetOpacity(0.0)
        self._plane_widget.GetOutlineProperty().SetOpacity(0.0)

        self._plotter.camera_position = "xy"

        # Create widgets
        self.component_select = pn.widgets.Select(
            name="Stress Component",
            options=STRESS_TYPES,
            value=STRESS_TYPES[0],
        )
        self.component_select.disabled = True
        self.ambient_slider = pn.widgets.FloatSlider(
            name="Ambient",
            start=0.0,
            end=1.0,
            value=self._actor.prop.ambient,
            step=0.05,
        )
        self.lighting_toggle = pn.widgets.Toggle(
            name="Lighting",
            value=self._actor.prop.lighting,
        )
        self.show_edges_toggle = pn.widgets.Toggle(name="Show Edges", value=True)
        self.show_edges_toggle.param.watch(self.update_show_edges, "value")

        self.colormap_select = pn.widgets.Select(
            name="Colormap",
            options=CMAPS,
            value=DEFAULT_CMAP,
        )

        # Create the X clip plane slider
        self.x_clip_slider = pn.widgets.FloatSlider(
            name="X Clip Plane",
            start=self._xrange[0],
            end=self._xrange[1],
            value=self._xrange[0],
            step=(self._xrange[1] - self._xrange[0]) / 100.0,
        )
        self.x_clip_slider.param.watch(self.update_clip_plane, "value")

        # Set up event watchers
        self.component_select.param.watch(self.update_component, "value")
        self.ambient_slider.param.watch(self.update_ambient, "value")
        self.lighting_toggle.param.watch(self.update_lighting, "value")
        self.colormap_select.param.watch(self.update_colormap, "value")

    def update_clip_plane(self, event: Event) -> None:
        x_position = event.new
        self._clip_callback((1, 0, 0), (x_position, 0.0, 0.0))
        self._plotter.render()

    def update_component(self, event: Event) -> None:
        # Map the selected stress component to its index
        idx = STRESS_TYPES.index(event.new)
        scalars_name = f"Nodal Stress-{idx}"

        # why won't this work?
        self._actor.mapper.SetArrayName(scalars_name)
        self._mesh.point_data.active_scalars_name = scalars_name

        # reset the scalars_range
        scalars = self._mesh[scalars_name]
        self._actor.mapper.scalar_range = (scalars.min(), scalars.max())
        self._plotter.render()

    def update_ambient(self, event: Event) -> None:
        self._actor.prop.ambient = event.new
        self._plotter.render()

    def update_show_edges(self, event: Event) -> None:
        self._actor.prop.show_edges = event.new
        self._plotter.render()

    def update_lighting(self, event: Event) -> None:
        self._actor.prop.lighting = event.new
        self._plotter.render()

    def update_colormap(self, event: Event) -> None:
        self._actor.mapper.lookup_table.cmap = event.new
        self._plotter.render()

    def __panel__(self):
        sidebar = pn.Column(
            pn.pane.Markdown("## Controls"),
            self.component_select,
            self.x_clip_slider,
            pn.layout.Divider(),
            pn.pane.Markdown("### Plotting Settings"),
            pn.layout.Row(self.lighting_toggle, self.show_edges_toggle),
            self.ambient_slider,
            self.colormap_select,
        )
        return pn.Row(sidebar, self._plotter_pane)

    # rewritten to return callback
    def add_mesh_clip_plane(
        self,
        mesh,
        normal="x",
        invert=False,
        widget_color=None,
        value=0.0,
        assign_to_axis=None,
        tubing=False,
        origin_translation=True,
        outline_translation=False,
        implicit=True,
        normal_rotation=True,
        crinkle=False,
        interaction_event="end",
        origin=None,
        **kwargs,
    ):
        """Clip a mesh using a plane widget.

        Add a mesh to the scene with a plane widget that is used to clip
        the mesh interactively.

        The clipped mesh is saved to the ``.plane_clipped_meshes``
        attribute on the plotter.

        Parameters
        ----------
        mesh : pyvista.DataSet or vtk.vtkAlgorithm
            The input dataset to add to the scene and clip or algorithm that
            produces said mesh.

        normal : str or tuple(float), optional
            The starting normal vector of the plane.

        invert : bool, optional
            Flag on whether to flip/invert the clip.

        widget_color : ColorLike, optional
            Either a string, RGB list, or hex color string.

        value : float, optional
            Set the clipping value along the normal direction.
            The default value is 0.0.

        assign_to_axis : str or int, optional
            Assign the normal of the plane to be parallel with a given
            axis.  Options are ``(0, 'x')``, ``(1, 'y')``, or ``(2,
            'z')``.

        tubing : bool, optional
            When using an implicit plane wiget, this controls whether
            or not tubing is shown around the plane's boundaries.

        origin_translation : bool, optional
            If ``False``, the plane widget cannot be translated by its
            origin and is strictly placed at the given origin. Only
            valid when using an implicit plane.

        outline_translation : bool, optional
            If ``False``, the box widget cannot be translated and is
            strictly placed at the given bounds.

        implicit : bool, optional
            When ``True``, a ``vtkImplicitPlaneWidget`` is used and
            when ``False``, a ``vtkPlaneWidget`` is used.

        normal_rotation : bool, optional
            Set the opacity of the normal vector arrow to 0 such that
            it is effectively disabled. This prevents the user from
            rotating the normal. This is forced to ``False`` when
            ``assign_to_axis`` is set.

        crinkle : bool, optional
            Crinkle the clip by extracting the entire cells along the clip.

        interaction_event : vtk.vtkCommand.EventIds, str, optional
            The VTK interaction event to use for triggering the
            callback. Accepts either the strings ``'start'``, ``'end'``,
            ``'always'`` or a ``vtk.vtkCommand.EventIds``.

            .. versionchanged:: 0.38.0
               Now accepts either strings or ``vtk.vtkCommand.EventIds``.

        origin : tuple(float), optional
            The starting coordinate of the center of the plane.

        **kwargs : dict, optional
            All additional keyword arguments are passed to
            :func:`Plotter.add_mesh` to control how the mesh is
            displayed.

        Returns
        -------
        vtk.vtkActor
            VTK actor of the mesh.

        Examples
        --------
        Shows an interactive plane used to clip the mesh and store it.

        >>> import pyvista as pv
        >>> from pyvista import examples
        >>> vol = examples.load_airplane()
        >>> pl = pv.Plotter()
        >>> _ = pl.add_mesh_clip_plane(vol, normal=[0, -1, 0])
        >>> pl.show(cpos=[-2.1, 0.6, 1.5])
        >>> pl.plane_clipped_meshes  # doctest:+SKIP

        For a full example see :ref:`plane_widget_example`.

        """
        if crinkle:
            raise NotImplementedError("Crinkle is not implemented")

        mesh, algo = algorithm_to_mesh_handler(
            add_ids_algorithm(mesh, point_ids=False, cell_ids=True)
        )

        name = kwargs.get("name", mesh.memory_address)
        rng = mesh.get_data_range(kwargs.get("scalars", None))
        kwargs.setdefault("render", False)
        kwargs.setdefault("reset_camera", False)
        kwargs.setdefault("clim", kwargs.pop("rng", rng))
        mesh.set_active_scalars(kwargs.get("scalars", mesh.active_scalars_name))
        if origin is None:
            origin = mesh.center

        self._plotter.add_mesh(
            outline_algorithm(algo),
            name=f"{name}-outline",
            opacity=0.0,
            reset_camera=False,
            render=False,
        )

        if isinstance(mesh, _vtk.vtkPolyData):
            clipper = _vtk.vtkClipPolyData()
        else:
            clipper = _vtk.vtkTableBasedClipDataSet()
        set_algorithm_input(clipper, algo)
        clipper.SetValue(value)
        clipper.SetInsideOut(invert)  # invert the clip if needed
        plane_clipped_mesh = _get_output(clipper)
        self._plotter.plane_clipped_meshes.append(plane_clipped_mesh)

        def callback(normal, loc):  # numpydoc ignore=GL08
            function = generate_plane(normal, loc)
            clipper.SetClipFunction(function)  # the implicit function
            clipper.Update()  # Perform the Cut
            clipped = pv.wrap(clipper.GetOutput())
            plane_clipped_mesh.shallow_copy(clipped)

        self._plotter.add_plane_widget(
            callback=callback,
            bounds=mesh.bounds,
            factor=1.25,
            normal=normal,
            color=widget_color,
            tubing=tubing,
            assign_to_axis=assign_to_axis,
            origin_translation=origin_translation,
            outline_translation=outline_translation,
            implicit=implicit,
            origin=origin,
            normal_rotation=normal_rotation,
            interaction_event=interaction_event,
            # target=target,
        )

        return callback, self._plotter.add_mesh(clipper, **kwargs)
