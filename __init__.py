# Re-export for Hermes directory-based install (~/.hermes/plugins/edge-pitch/).
# Hermes loads this __init__.py and sets __path__ so that from .edge_pitch works.
# For pip install: the hermes_agent.plugins entry-point points directly to edge_pitch.
from .edge_pitch import EdgePitchProvider, main, register  # noqa: F401
