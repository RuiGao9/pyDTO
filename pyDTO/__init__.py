# This is a crucial line: it brings the functions from api.py to the top level of the package, 
# allowing users to call pyDTO.get_dist and pyDTO.plot_dto directly.
from .api import get_dist
from .api import plot_dto

# This allows users to directly call pyDTO.get_dist and pyDTO.plot_dto without needing to import from submodules.
__all__ = ["get_dist", "plot_dto"]