import os
from pathlib import Path
import geopandas as gpd


def load_ca_data():
    MODULE_DIR = Path(__file__).resolve().parent
    SHP_PATH = MODULE_DIR / "data" / "california_boundary.shp"

    if not SHP_PATH.exists():
        raise FileNotFoundError(f"Missing shapefile at: {SHP_PATH}")
        
    gdf = gpd.read_file(SHP_PATH)
    gdf = gdf.to_crs("EPSG:4326")  # Using WGS84 coordinate system

    return gdf.unary_union