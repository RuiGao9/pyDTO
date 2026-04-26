from .data_manager import load_ca_data
from .engine import DTOEngine
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, LineString


# 1. Initialize data and engine on module load (Singleton Pattern)
# This way, users don't need to repeatedly load the heavy Shapefile when calling get_dist multiple times
try:
    _CA_POLYGON = load_ca_data()
    _ENGINE = DTOEngine()
except Exception as e:
    print(f"Error initializing pyDTO: {e}")
    _CA_POLYGON = None
    _ENGINE = None

def get_dist(lon, lat, unit='km'):
    """
    Main processing flow:
    1. Receive longitude and latitude input
    2. Call the engine to calculate distances to the boundary in four directions
    3. Return the formatted results
    """

    if _CA_POLYGON is None:
        return {"error": "pyDTO failed to initialize. Check if shapefile is missing."}
    
    p = Point(lon, lat)
    if not _CA_POLYGON.contains(p):
        raise ValueError(f"The input coordinates ({lon}, {lat}) are outside the California state boundary. "
                         "This tool only supports locations within California.")
    # Modify this part. Based on users' requests to decide if the information should be printed or not.
    # print(f"DEBUG: Location is verified within California.")

    # Call the calculation logic in engine.py
    raw_distances = _ENGINE.get_distances(lon, lat, _CA_POLYGON)
    
    # Unit conversion logic (default returns km, as it's more intuitive for state boundary distances)
    divisor = 1000.0 if unit == 'km' else 1.0
    
    formatted_dist = {}
    for direction, value in raw_distances.items():
        if value is not None:
            formatted_dist[direction] = round(value / divisor, 2)
        else:
            formatted_dist[direction] = None

    return {
        "location": {"lon": lon, "lat": lat},
        "unit": unit,
        "distances": formatted_dist
    }


def plot_dto(lon, lat, results=None):
    """
    Visualize the California boundary, the target point, and the four directions' rays/spans.
    """
    # 1. Loading the California boundary data for plotting
    from .api import _CA_POLYGON
    if _CA_POLYGON is None:
        print("Error: Boundary data not loaded.")
        return

    fig, ax = plt.subplots(figsize=(10, 12))
    
    # 2. Plot CA boundary as the background layer
    gdf = gpd.GeoSeries([_CA_POLYGON], crs="EPSG:4326")
    gdf.plot(ax=ax, color='#f0f0f0', edgecolor='#444444', linewidth=1, label='CA Boundary')
    
    # 3. Plot the point of interest
    ax.scatter(lon, lat, color='red', s=100, zorder=5, label=f'Location ({lon}, {lat})')
    
    # 4. Plot the north-south range lines
    min_x, min_y, max_x, max_y = _CA_POLYGON.bounds
    ax.vlines(x=lon, ymin=min_y, ymax=max_y, color='blue', linestyle='--', alpha=0.6, label='N-S Range')
    
    # 5. Plot the east-west rays (horizontal lines)
    # Simplely indicates lines to illustrate the boundary-finding process
    ax.hlines(y=lat, xmin=min_x, xmax=max_x, color='green', linestyle=':', alpha=0.6, label='E-W Rays')

    ax.set_title("pyDTO Geographic Context Visualization", fontsize=12)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_aspect('equal')
    
    plt.show()
