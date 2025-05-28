"""
参数处理工具包

功能：
- 提供 post 请求 body 字段过滤方法，便于用例只传递需要的字段。
"""
from typing import Dict, List, Any

def filter_post_body_fields(body: Dict[str, Any], fields: List[str], path: List[str] = None) -> Dict[str, Any]:
    """
    支持指定嵌套路径的字段过滤，并将过滤结果嵌套回原路径
    :param body: 原始请求体 dict
    :param fields: 需要保留的字段名列表
    :param path: 需要过滤的嵌套路径（如 ["params", "request"]）
    :return: 只包含指定字段的新 dict，嵌套回 path
    """
    if path and len(path) > 0:
        p = path[0]
        sub_body = body.get(p, {})
        filtered = filter_post_body_fields(sub_body, fields, path[1:])
        return {p: filtered}
    else:
        return {k: v for k, v in body.items() if k in fields}

# 示例用例
def _demo():
    swagger_body = {
        "params": {
            "request": {
                "id": 1,
                "name": "test",
                "desc": "desc"
            }
        }
    }
    fields = ["id"]
    filtered = filter_post_body_fields(swagger_body, fields, path=["params", "request"])
    print(filtered)  # 输出: {'params': {'request': {'id': 1, 'name': 'test'}}}

if __name__ == "__main__":
    _demo() 
    
    