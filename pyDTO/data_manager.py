import os
import geopandas as gpd


def load_ca_data():
    base_path = os.path.dirname(__file__)
    # Back to the root directory, then into the data folder
    shp_path = os.path.normpath(os.path.join(base_path, "..", "data", "CA_Counties.shp"))
    
    print(f"DEBUG: Trying to load file: {shp_path}") 
    
    if not os.path.exists(shp_path):
        print(f"DEBUG: Errors! No such file: {shp_path}")
        return None
    
    gdf = gpd.read_file(shp_path)
    gdf = gdf.to_crs("EPSG:4326")  # Using WGS84 coordinate system

    return gdf.unary_union