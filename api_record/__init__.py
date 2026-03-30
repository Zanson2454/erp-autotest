# -*- coding: utf-8 -*-
"""API record tooling package.

中文说明：
- 保留 `__init__.py` 的目的：让 `api_record/` 成为一个可导入的 Python 包。
- 典型收益：
  - 便于后续把录制相关工具做成可复用模块（例如 `from api_record import recorder`）。
  - 在某些运行环境/工具链中，包结构更稳定（相对路径与资源定位更可控）。
- 该文件本身不承载业务逻辑，属于结构性文件。
"""

