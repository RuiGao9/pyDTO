from .data_manager import load_ca_data
from .engine import DTOEngine

# 1. 在模块加载时预读数据和初始化引擎 (Singleton Pattern)
# 这样用户多次调用 get_dist 时，不需要重复加载繁重的 Shapefile
try:
    _CA_POLYGON = load_ca_data()
    _ENGINE = DTOEngine()
except Exception as e:
    print(f"Error initializing pyDTO: {e}")
    _CA_POLYGON = None
    _ENGINE = None

def get_dist(lon, lat, unit='km'):
    """
    主处理流程：
    1. 接收经纬度输入
    2. 调用引擎计算四个方向到边界的距离
    3. 返回格式化的结果
    """

    from shapely.geometry import Point

    p = Point(lon, lat)
    print(f"DEBUG: Received location is within California state? {_CA_POLYGON.contains(p)}")
    if _CA_POLYGON is None:
        return {"error": "Data not loaded correctly."}

    # 调用 engine.py 中的计算逻辑
    raw_distances = _ENGINE.get_distances(lon, lat, _CA_POLYGON)
    
    # 单位换算逻辑 (默认返回 km，因为对于州界距离来说 km 更直观)
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