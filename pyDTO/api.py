from .data_manager import load_ca_data
from .engine import DTOEngine
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, LineString


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


def plot_dto(lon, lat, results=None):
    """
    可视化加州边界、目标点以及四个方向的射线/跨度。
    """
    # 1. 加载边界数据
    from .api import _CA_POLYGON
    if _CA_POLYGON is None:
        print("Error: Boundary data not loaded.")
        return

    fig, ax = plt.subplots(figsize=(10, 12))
    
    # 2. 绘制加州背景
    gdf = gpd.GeoSeries([_CA_POLYGON], crs="EPSG:4326")
    gdf.plot(ax=ax, color='#f0f0f0', edgecolor='#444444', linewidth=1, label='CA Boundary')
    
    # 3. 绘制目标点
    ax.scatter(lon, lat, color='red', s=100, zorder=5, label=f'Location ({lon}, {lat})')
    
    # 4. 绘制南北极值线 (垂直线)
    min_x, min_y, max_x, max_y = _CA_POLYGON.bounds
    ax.vlines(x=lon, ymin=min_y, ymax=max_y, color='blue', linestyle='--', alpha=0.6, label='N-S Range')
    
    # 5. 绘制东西射线 (水平线)
    # 简单的示意线，展示寻找边界的过程
    ax.hlines(y=lat, xmin=min_x, xmax=max_x, color='green', linestyle=':', alpha=0.6, label='E-W Rays')

    # 6. 图表装饰
    ax.set_title("pyDTO Geographic Context Visualization", fontsize=15)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_aspect('equal')
    
    plt.show()