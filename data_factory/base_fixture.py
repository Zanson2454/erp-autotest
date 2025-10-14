# """基础工具类 - 所有 fixture 的父类"""
# from datetime import datetime
# import random
# import string


# class BaseFixture:
#     """提供公共方法"""
    
#     @staticmethod
#     def generate_code(prefix: str, length: int = 20) -> str:
#         """生成唯一编码"""
#         timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#         remaining = length - len(prefix) - 14
#         if remaining > 0:
#             suffix = ''.join(random.choices(string.digits, k=remaining))
#             return f"{prefix}{timestamp}{suffix}"
#         return f"{prefix}{timestamp}"