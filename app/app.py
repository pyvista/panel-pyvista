import numpy as np
import pandas as pd
import panel as pn
from pyvista_panel import PyVistaPlotter

import hvplot.pandas  # noqa


# Generate sine wave data
def generate_sine_wave(freq, amp, phase, num_points=500):
    x = np.linspace(0, 10, num_points)
    y = amp * np.sin(2 * np.pi * freq * x + phase)
    return pd.DataFrame({"x": x, "y": y})


# Initial parameters
frequency = pn.widgets.FloatSlider(
    name="Frequency", start=0.1, end=5, value=1, step=0.1
)
amplitude = pn.widgets.FloatSlider(
    name="Amplitude", start=0.1, end=10, value=1, step=0.1
)
phase = pn.widgets.FloatSlider(name="Phase", start=0, end=2 * np.pi, value=0, step=0.1)


@pn.depends(frequency, amplitude, phase)
def sine_wave_plot(freq, amp, phase):
    data = generate_sine_wave(freq, amp, phase)
    return data.hvplot.line(x="x", y="y", width=600, height=400, line_width=3).opts(
        title="Interactive Sine Wave",
        ylabel="Amplitude",
        xlabel="Time",
        # yformatter=PrintfTickFormatter(format="%.2f"),
    )


# Servable Layout
sine_col = pn.Column(
    "### Sine Wave Interactive Plot", frequency, amplitude, phase, sine_wave_plot
)

pv_plotter = PyVistaPlotter()

pn.Tabs(
    ("PyVista", pv_plotter),
    ("Sine Plot", sine_col),
).servable()
