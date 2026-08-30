"""A reusable maze generator and solver."""

from .generator import MazeGenerator
from .path_finder import solve, path_cells
from .config_parser import ConfigParser

__version__ = "1.0.0"

__all__ = [
    "MazeGenerator",
    "solve",
    "path_cells",
    "ConfigParser",
]
