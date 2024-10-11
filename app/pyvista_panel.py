from typing import Any, Dict, Union, List, Optional

from param.parameterized import Event
import numpy as np
import panel as pn
import pyvista as pv
from pyvista.plotting.opts import InterpolationType
from pyvista.plotting import Actor

from pyvista import demos as pv_demos
from pyvista.plotting import Plotter
from common import DEFAULT_BACKEND, show_panel, CMAPS


class PyVistaPlotter(pn.viewable.Viewer):
    def __init__(self, jupyter_backend: str = DEFAULT_BACKEND, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._plotter = Plotter(off_screen=True, notebook=True)
        self._plotter.add_axes()  # type: ignore
        self._plotter_pane = show_panel(self.plotter, jupyter_backend=jupyter_backend)

        # Set up actors
        pl = pv_demos.plot_logo(just_return_plotter=True)
        for name, actor in pl.actors.items():
            actor.prop.ambient = 0.3
            self._plotter.add_actor(actor, name=name)

        self._plotter.camera_position = "xy"

        # bounding box actor
        self.bounding_box_actor: Optional[Actor] = None

        # Actor selection widget
        self.actor_select = pn.widgets.Select(
            name="Select Actor", options=self.actor_names
        )

        # Initialize property widgets
        self._initialize_property_widgets()

        # Define callbacks
        self.actor_select.param.watch(self.update_actor_widgets, "value")

        # Initialize actor widgets
        if self.actor_select.value:
            self.update_actor_widgets({"new": self.actor_select.value})

    def _initialize_property_widgets(self):
        # Visibility
        self.visibility_toggle = pn.widgets.Toggle(name="Visible", value=True)

        # Colors
        self.color_picker = pn.widgets.ColorPicker(name="Color", value="#FFFFFF")
        self.ambient_color_picker = pn.widgets.ColorPicker(value="#FFFFFF")
        self.diffuse_color_picker = pn.widgets.ColorPicker(value="#FFFFFF")
        self.specular_color_picker = pn.widgets.ColorPicker(value="#FFFFFF")
        self.edge_color_picker = pn.widgets.ColorPicker(value="#FFFFFF")

        self.color_grid = pn.GridSpec()
        self.color_grid[0, 0] = pn.pane.Markdown("**Color**")
        self.color_grid[0, 1] = self.ambient_color_picker

        self.color_grid[1, 0] = pn.pane.Markdown("**Ambient Color**")
        self.color_grid[1, 1] = self.diffuse_color_picker

        self.color_grid[2, 0] = pn.pane.Markdown("**Diffuse Color**")
        self.color_grid[2, 1] = self.diffuse_color_picker

        self.color_grid[3, 0] = pn.pane.Markdown("**Specular Color**")
        self.color_grid[3, 1] = self.specular_color_picker

        self.color_grid[4, 0] = pn.pane.Markdown("**Edge Color**")
        self.color_grid[4, 1] = self.edge_color_picker

        # Line and Point Size
        self.line_width_slider = pn.widgets.FloatSlider(
            name="Line Width", start=1.0, end=10.0, value=1.0
        )
        self.point_size_slider = pn.widgets.FloatSlider(
            name="Point Size", start=1.0, end=20.0, value=5.0
        )

        # Toggles and Selectors
        self.show_edges_toggle = pn.widgets.Toggle(name="Show Edges", value=False)
        self.lighting_toggle = pn.widgets.Toggle(name="Lighting", value=True)
        self.interpolation_select = pn.widgets.Select(
            name="Interpolation",
            options=[item.name for item in InterpolationType],
            value="Phong",
        )
        self.style_select = pn.widgets.Select(
            name="Style", options=["Surface", "Wireframe", "Points"], value="Surface"
        )

        # Scalars
        self.opacity_slider = pn.widgets.FloatSlider(
            name="Opacity", start=0.0, end=1.0, value=1.0
        )
        self.ambient_slider = pn.widgets.FloatSlider(
            name="Ambient", start=0.0, end=1.0, value=0.3
        )
        self.diffuse_slider = pn.widgets.FloatSlider(
            name="Diffuse", start=0.0, end=1.0, value=1.0
        )
        self.specular_slider = pn.widgets.FloatSlider(
            name="Specular", start=0.0, end=1.0, value=0.0
        )
        self.specular_power_slider = pn.widgets.FloatSlider(
            name="Specular Power", start=0.0, end=100.0, value=1.0
        )

        # Watchers for property changes
        self.visibility_toggle.param.watch(self.update_visibility, "value")
        self.color_picker.param.watch(self.update_color, "value")
        self.ambient_color_picker.param.watch(self.update_ambient_color, "value")
        self.diffuse_color_picker.param.watch(self.update_diffuse_color, "value")
        self.specular_color_picker.param.watch(self.update_specular_color, "value")
        self.edge_color_picker.param.watch(self.update_edge_color, "value")
        self.opacity_slider.param.watch(self.update_opacity, "value")
        self.ambient_slider.param.watch(self.update_ambient, "value")
        self.diffuse_slider.param.watch(self.update_diffuse, "value")
        self.specular_slider.param.watch(self.update_specular, "value")
        self.specular_power_slider.param.watch(self.update_specular_power, "value")
        self.line_width_slider.param.watch(self.update_line_width, "value")
        self.point_size_slider.param.watch(self.update_point_size, "value")
        self.show_edges_toggle.param.watch(self.update_show_edges, "value")
        self.lighting_toggle.param.watch(self.update_lighting, "value")
        self.interpolation_select.param.watch(self.update_interpolation, "value")
        self.style_select.param.watch(self.update_style, "value")

        # Scalars section
        self.scalar_range_slider = pn.widgets.RangeSlider(
            name="Scalar Range", start=0.0, end=1.0, value=(0.0, 1.0)
        )
        self.scalar_type_select = pn.widgets.Select(
            name="Scalar Type", options=["None", "Point", "Cell"], value="None"
        )
        self.interpolate_before_map_toggle = pn.widgets.Toggle(
            name="Interpolate Before Map", value=True
        )
        self.active_scalar_select = pn.widgets.Select(
            name="Active Scalars", options=["None"], value="None"
        )

        # Watchers for scalar property changes
        self.scalar_range_slider.param.watch(self.update_scalar_range, "value")
        self.scalar_type_select.param.watch(self.update_scalar_type, "value")
        self.interpolate_before_map_toggle.param.watch(
            self.update_interpolate_before_map, "value"
        )
        self.active_scalar_select.param.watch(self.update_active_scalars, "value")

        # Dropdown and watcher to select colormap
        self.colormap_select = pn.widgets.Select(
            name="Colormap", options=CMAPS, value=pv.global_theme.cmap
        )
        self.colormap_select.param.watch(self.update_colormap, "value")

    def update_bounding_box(self, actor: Actor) -> None:
        # Remove previous bounding box actor if it exists
        if self.bounding_box_actor is not None:
            self._plotter.remove_actor(self.bounding_box_actor)
            self.bounding_box_actor = None

        # Create bounding box for the selected actor
        if actor.mapper and actor.mapper.dataset:
            dataset = actor.mapper.dataset
            outline = dataset.outline()
            self.bounding_box_actor = self._plotter.add_mesh(
                outline, color="red", line_width=2, name="BoundingBox"
            )

    def update_actor_widgets(self, event: Union[Event, Dict]) -> None:
        if isinstance(event, Event):
            actor_name = event.obj.value
        else:  # dictionary
            actor_name = event["new"]

        actor: Actor = self._plotter.actors[actor_name]
        if not hasattr(actor, "prop"):
            return
        prop = actor.prop

        # add a bounding box actor
        self.update_bounding_box(actor)

        # Update widgets with current actor properties
        self.visibility_toggle.value = actor.visibility

        # Colors
        self.color_picker.value = prop.color.hex_rgb
        self.ambient_color_picker.value = prop.ambient_color.hex_rgb
        self.diffuse_color_picker.value = prop.diffuse_color.hex_rgb
        self.specular_color_picker.value = prop.specular_color.hex_rgb
        self.edge_color_picker.value = prop.edge_color.hex_rgb

        # lighting
        self.opacity_slider.value = prop.opacity
        self.ambient_slider.value = prop.ambient
        self.diffuse_slider.value = prop.diffuse
        self.specular_slider.value = prop.specular
        self.specular_power_slider.value = prop.specular_power

        # Line and Point Size
        self.line_width_slider.value = prop.line_width
        self.point_size_slider.value = prop.point_size

        # Toggles and Selectors
        self.show_edges_toggle.value = prop.show_edges
        self.lighting_toggle.value = prop.lighting
        self.interpolation_select.value = prop.interpolation.name
        self.style_select.value = prop.style

        showing_lines = prop.show_edges or prop.style == "Wirefame"
        self.line_width_slider.disabled = not showing_lines
        self.point_size_slider.disabled = prop.style != "Points"

        # scalars visibility
        mapper = actor.mapper
        if mapper is not None:
            mm = mapper.scalar_map_mode.capitalize()
            self.scalar_type_select.value = "None" if mm == "Default" else mm

        disabled = self.scalar_type_select.value == "None"
        if disabled:
            self.interpolate_before_map_toggle.value = True
            self.scalar_type_select.value = "None"
            self.scalar_range_slider.start = 0.0
            self.scalar_range_slider.end = 1.0
            self.scalar_range_slider.value = (0.0, 1.0)
            self.active_scalar_select.options = ["None"]
            self.active_scalar_select.value = "None"
        else:
            # enable the widgets
            self.interpolate_before_map_toggle.value = mapper.interpolate_before_map

            mm = mapper.scalar_map_mode.capitalize()

            # Update scalar range slider
            scalar_range = mapper.scalar_range
            if scalar_range is not None:
                self.scalar_range_slider.start = scalar_range[0]
                self.scalar_range_slider.end = scalar_range[1]
                self.scalar_range_slider.value = scalar_range
            else:
                self.scalar_range_slider.start = 0.0
                self.scalar_range_slider.end = 1.0
                self.scalar_range_slider.value = (0.0, 1.0)

            # Update active scalars options
            dataset = mapper.dataset
            point_scalars = list(dataset.point_data.keys())
            cell_scalars = list(dataset.cell_data.keys())

            # Update scalar type options based on available scalars
            available_scalar_types = ["None"]
            if point_scalars:
                available_scalar_types.append("Point")
            if cell_scalars:
                available_scalar_types.append("Cell")
            self.scalar_type_select.options = available_scalar_types

            # Set active scalar name
            active_scalar_name = dataset.active_scalars_name
            self.active_scalar_select.value = (
                active_scalar_name if active_scalar_name else "None"
            )

            # add available scalars
            if mapper.scalar_map_mode == "cell":
                self.active_scalar_select.options = cell_scalars
            elif mapper.scalar_map_mode == "point":
                self.active_scalar_select.options = point_scalars
            else:
                self.active_scalar_select.options = ["None"]

            # update colormap
            self.colormap_select.value = mapper.cmap

        # disable/disable the widgets
        self.interpolate_before_map_toggle.disabled = disabled
        self.scalar_range_slider.disabled = disabled
        self.scalar_range_slider.disabled = disabled
        self.scalar_range_slider.disabled = disabled
        self.active_scalar_select.disabled = disabled
        self.colormap_select.disabled = disabled

    def update_visibility(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.SetVisibility(event.new)
        self._plotter.render()

    def update_color(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.color = event.new
        self._plotter.render()

    def update_ambient_color(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.ambient_color = event.new
        self._plotter.render()

    def update_diffuse_color(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.diffuse_color = event.new
        self._plotter.render()

    def update_specular_color(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.specular_color = event.new
        self._plotter.render()

    def update_edge_color(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.edge_color = event.new
        self._plotter.render()

    def update_opacity(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.opacity = event.new
        self._plotter.render()

    def update_ambient(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.ambient = event.new
        self._plotter.render()

    def update_diffuse(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.diffuse = event.new
        self._plotter.render()

    def update_specular(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.specular = event.new
        self._plotter.render()

    def update_specular_power(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.specular_power = event.new
        self._plotter.render()

    def update_line_width(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.line_width = event.new
        self._plotter.render()

    def update_point_size(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.point_size = event.new
        self._plotter.render()

    def update_show_edges(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.show_edges = event.new
        self._plotter.render()

    def update_lighting(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.lighting = event.new
        self._plotter.render()

    def update_interpolation(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.interpolation = getattr(InterpolationType, event.new)
        self._plotter.render()

    def update_style(self, event: Event):
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.prop.style = event.new
        self._plotter.render()

    def update_scalar_range(self, event: Event) -> None:
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.mapper.scalar_range = event.new
        self._plotter.render()

    def update_scalar_type(self, event: Event) -> None:
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        mapper = actor.mapper
        dataset = mapper.dataset

        # Update active scalars options based on scalar type
        event_sel = event.new.lower()
        point_data_keys = list(dataset.point_data.keys())
        cell_data_keys = list(dataset.cell_data.keys())
        if event_sel == "point":
            scalars_options = point_data_keys

        elif event_sel == "cell":
            scalars_options = cell_data_keys
        else:
            scalars_options = ["None"]

        disabled = event_sel not in ["point", "cell"]
        self.interpolate_before_map_toggle.disabled = disabled
        self.scalar_range_slider.disabled = disabled
        self.scalar_range_slider.disabled = disabled
        self.scalar_range_slider.disabled = disabled
        self.active_scalar_select.disabled = disabled
        self.colormap_select.disabled = disabled

        self.active_scalar_select.options = scalars_options

        # Set active scalar name to the first available active scalar
        if dataset.active_scalars_name not in scalars_options:
            self.active_scalar_select.value = scalars_options[0]

        # Update the mapper's scalar_map_mode
        mm = "default" if event_sel not in ["point", "cell"] else event_sel
        mapper.scalar_map_mode = mm
        self._plotter.render()

    def update_interpolate_before_map(self, event: Event) -> None:
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.mapper.interpolate_before_map = event.new
        self._plotter.render()

    def update_active_scalars(self, event: Event) -> None:
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        dataset = actor.mapper.dataset
        new_scalars = None if event.new == "None" else event.new
        mapper = actor.mapper
        if mapper.GetArrayName() != new_scalars:
            # mapper.SetArrayName(new_scalars)
            try:
                dataset.active_scalars_name = new_scalars
            except KeyError:
                print(f"Invalid scalars name {new_scalars}")
                return

            if new_scalars:
                actor.mapper.scalar_visibility = True
                rng = (dataset.active_scalars.min(), dataset.active_scalars.max())
                # Trame bug: active scalars must be float
                if not np.issubdtype(dataset.active_scalars.dtype, np.floating):
                    dataset[new_scalars] = dataset[new_scalars].astype(float)
                actor.mapper.scalar_range = rng
                actor.mapper.lookup_table.cmap = self.colormap_select.value
            else:
                actor.mapper.scalar_visibility = False

        self._plotter.render()

    def update_colormap(self, event: Event) -> None:
        actor_name = self.actor_select.value
        actor = self._plotter.actors[actor_name]
        actor.mapper.lookup_table.cmap = event.new
        self._plotter.render()

    @property
    def actor_names(self) -> List[str]:
        actor_names: List[str] = []
        for actor_name, actor in self._plotter.actors.items():
            if hasattr(actor, "prop"):
                actor_names.append(actor_name)
        return actor_names

    @property
    def plotter(self) -> Plotter:
        return self._plotter

    def __panel__(self):
        sidebar = pn.Column(
            "## Actor Properties",
            self.actor_select,
            pn.layout.Divider(),
            pn.pane.Markdown("### Options"),
            self.visibility_toggle,
            self.interpolation_select,
            self.style_select,
            self.show_edges_toggle,
            pn.layout.Divider(),
            pn.pane.Markdown("### Colors"),
            self.color_grid,
            pn.layout.Divider(),
            pn.pane.Markdown("### Lighting"),
            self.lighting_toggle,
            self.opacity_slider,
            self.ambient_slider,
            self.diffuse_slider,
            self.specular_slider,
            self.specular_power_slider,
            pn.layout.Divider(),
            pn.pane.Markdown("### Sizes"),
            self.line_width_slider,
            self.point_size_slider,
            pn.layout.Divider(),
            pn.pane.Markdown("### Scalars"),
            self.scalar_type_select,
            self.active_scalar_select,
            self.interpolate_before_map_toggle,
            self.scalar_range_slider,
            self.colormap_select,
            scroll=True,
        )

        return pn.Row(sidebar, self._plotter_pane)
