import panel as pn


class GlobalStateMixin:
    """Mixin to propagate the app instance and state to all components"""

    @property
    def app(self):
        return pn.state.cache["app"]
