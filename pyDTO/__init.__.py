# 这一行非常重要：它把 api.py 里的函数拉到了包的最顶层
from .api import get_dist

# 这样用户可以直接通过 pyDTO.get_dist 调用
__all__ = ["get_dist"]