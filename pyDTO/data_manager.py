import geopandas as gpd
import os

def load_ca_data():
    # head to data folder, and find ".shp"
    base_path = os.path.dirname(__file__)
    # back to root folder, get into data folder again
    shp_path = os.path.join(base_path, "..", "data", "CA_Counties.shp")
    
    if not os.path.exists(shp_path):
        raise FileNotFoundError(f"Cannot find reference map: {shp_path}")
        
    ca_poly = gpd.read_file(shp_path)
    
    # core process: extract the shapefile
    # only one record for the shapefile
    # ca_poly = gdf.unary_union
    return ca_poly