import pyproj
from shapely.geometry import Point, LineString
from shapely.ops import transform


class DTOEngine:
    def __init__(self):
        # Define coordinate transformation: from WGS84 lat/lon to California Albers (EPSG:3310)
        self.wgs84 = pyproj.CRS('EPSG:4326')
        self.ca_albers = pyproj.CRS('EPSG:3310')
        self.transformer = pyproj.Transformer.from_crs(self.wgs84, self.ca_albers, always_xy=True).transform

    def get_distances(self, lon, lat, polygon):
        p_orig = Point(lon, lat)
        boundary = polygon.boundary
        
        # Obtaining the bounding box of the California polygon to determine the extreme latitudes and longitudes
        min_x, min_y, max_x, max_y = polygon.bounds
        
        results = {}
        p_start_proj = transform(self.transformer, p_orig)

        # --- Modifying the calculation algorithm to the extreme north and south points from the north and south boundaries: calculation the distance to the extreme points ---
        # Making sure that the longitude is the same, only the latitude is different, to ensure that the distance is calculated along the north-south direction
        p_north_extreme = Point(lon, max_y)
        p_south_extreme = Point(lon, min_y)
        
        p_north_proj = transform(self.transformer, p_north_extreme)
        p_south_proj = transform(self.transformer, p_south_extreme)
        
        results["North"] = round(p_start_proj.distance(p_north_proj), 2)
        results["South"] = round(p_start_proj.distance(p_south_proj), 2)

        # --- For the algorithm to the east and west state boundary, keeping the logic of using a ray to touch the boundary ---
        # Constructing east-west rays (spanning 15 degrees to ensure coverage)
        rays = {
            "East":  LineString([(lon, lat), (lon + 15, lat)]),
            "West":  LineString([(lon, lat), (lon - 15, lat)])
        }

        for direction, ray in rays.items():
            intersection = ray.intersection(boundary)
            
            if intersection.is_empty:
                results[direction] = None
                continue
                
            if intersection.geom_type == 'MultiPoint':
                if direction == "West":
                    # Key logic: For the west direction, we take the westernmost intersection point, which directly touches the ocean coastline
                    target_p = min(intersection.geoms, key=lambda p: p.x)
                else:
                    # For the east direction, we take the closest intersection point
                    target_p = min(intersection.geoms, key=lambda p: p_orig.distance(p))
            else:
                target_p = intersection
            
            p_end_proj = transform(self.transformer, target_p)
            results[direction] = round(p_start_proj.distance(p_end_proj), 2)
            
        return results