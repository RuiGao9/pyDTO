import pyproj
from shapely.geometry import Point, LineString
from shapely.ops import transform

class DTOEngine:
    def __init__(self):
        # 定义坐标转换：从经纬度转为加州标准的 Albers 米制投影 (EPSG:3310)
        self.wgs84 = pyproj.CRS('EPSG:4326')
        self.ca_albers = pyproj.CRS('EPSG:3310')
        self.transformer = pyproj.Transformer.from_crs(self.wgs84, self.ca_albers, always_xy=True).transform

    def get_distances(self, lon, lat, polygon):
        """
        核心逻辑：从给定点向四个方向发射射线，计算与边界的交点距离。
        """
        p_orig = Point(lon, lat)
        boundary = polygon.boundary
        
        # 构造四条射线（约 500 公里长，足以覆盖加州）
        # 线条严格平行于经纬线（即平行于赤道和本初子午线）
        rays = {
            "North": LineString([(lon, lat), (lon, lat + 5)]),
            "South": LineString([(lon, lat), (lon, lat - 5)]),
            "East":  LineString([(lon, lat), (lon + 6, lat)]),
            "West":  LineString([(lon, lat), (lon - 6, lat)])
        }
        
        results = {}
        p_start_proj = transform(self.transformer, p_orig)

        for direction, ray in rays.items():
            intersection = ray.intersection(boundary)
            
            if intersection.is_empty:
                results[direction] = None
                continue
                
            # 处理多点交点的情况（例如射线穿过了内海或复杂的海岸线）
            if intersection.geom_type == 'MultiPoint':
                if direction == "West":
                    # 针对你的需求优化：取最西边的点（x 坐标最小的点）
                    # 这样可以无视旧金山湾内部的线条，直接到达真正的太平洋沿岸
                    target_p = min(intersection.geoms, key=lambda p: p.x)
                else:
                    # 其他方向取最近的交点
                    target_p = min(intersection.geoms, key=lambda p: p_orig.distance(p))
            else:
                target_p = intersection
            
            # 将交点转换为投影坐标并计算实际地面距离（米）
            p_end_proj = transform(self.transformer, target_p)
            results[direction] = p_start_proj.distance(p_end_proj)
            
        return results