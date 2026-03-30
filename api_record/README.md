这里有一份完整的 **API 录制与 AI 转化方案** 说明文档。你可以直接复制到项目的 `api_record/README.md` 中。

---

# API 录制与 AI 转化方案 (cURL 驱动版)

## 🎯 核心理念
**“录制只留逻辑，AI 完成重构”**。
通过 `mitmproxy` 将手工操作捕获为标准的 **cURL Markdown 集合**，利用 **Cursor (AI)** 结合项目定制的 `pytest` 模板规则，一键生成高质量、符合业务规范的自动化用例。

---

## 📂 目录结构

```text
api_record/
├── recorder.py             # mitmproxy 插件：捕获请求并导出为 cURL Markdown
├── start_recorder.py       # 启动器：配置代理并运行 mitmdump
├── recorder_config.json    # 过滤配置：Host 白名单、静态资源黑名单
└── raw_curls/              # 存放录制产物（原始 cURL 逻辑集）
    └── flow_example.md     # 录制生成的中间文件，用于交给 AI 转化
```

---

## 🛠 录制器实现 (`recorder.py`)

录制器不再生成复杂的 Python 代码，仅输出纯净的 cURL 块：

```python
import json
from mitmproxy import http

class CurlRecorder:
    def __init__(self):
        with open("api_record/recorder_config.json", "r") as f:
            self.config = json.load(f)
        self.output_file = f"api_record/raw_curls/recorded_flow.md"

    def request(self, flow: http.HTTPFlow):
        # 1. 过滤逻辑
        host = flow.request.pretty_host
        path = flow.request.path
        if self.config["allowed_hosts"] and host not in self.config["allowed_hosts"]:
            return
        if any(ext in path for ext in [".js", ".css", ".png", ".jpg", "/metrics"]):
            return

        # 2. 构造 cURL 字符串
        method = flow.request.method
        url = flow.request.pretty_url
        headers = " ".join([f'-H "{k}: {v}"' for k, v in flow.request.headers.items() 
                           if k.lower() not in ["cookie", "authorization", "content-length"]])
        data = flow.request.content.decode("utf-8") if flow.request.content else ""
        
        curl = f"curl -X {method} '{url}' {headers}"
        if data:
            curl += f" -d '{data}'"

        # 3. 追加到 Markdown
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(f"### Step: {path}\n")
            f.write(f"```bash\n{curl}\n```\n\n")

addons = [CurlRecorder()]
```

---

## 🤖 AI 转化工作流 (Cursor/Gemini)

这是解决“手动迁移难”的关键。将 `raw_curls/` 下的文件交给 AI，并配合以下指令：

### 1. 准备上下文
确保 Cursor 已经索引了你的 `ERP自动化测试项目 - 用例模板参考`（即你上个回复中的文档）。

### 2. 转换指令 (Prompt)
在 Cursor 中全选录制出的 cURL Markdown，输入以下指令：

> **“请根据项目 `用例模板参考` 规范，将这些 cURL 转化为 `TestModuleManagement` 类中的测试方法。”**
> 
> **转换要求：**
> 1. **鉴权脱敏**：忽略 cURL 里的 Header，统一使用 `self.standard_api_call`。
> 2. **数据关联**：自动识别 URL 或 Body 中的硬编码 ID。如果是前序接口返回的，请使用变量关联（例如 `self.xxx_id = extracted_id`）。
> 3. **基础数据**：从 `self.init_data` 或 `self.md_cache_data` 获取 `orgId`, `currencyId` 等基础配置。
> 4. **断言**：添加标准响应断言 `self.assert_util.assert_response_data(response)`。
> 5. **清理**：在 `teardown_class` 中补充对应的 `db.delete` 逻辑。

---

## ✅ 方案优势对比

| 维度 | 传统录制回放 | **本方案 (cURL + AI)** |
| :--- | :--- | :--- |
| **脚本稳定性** | 极差（Cookie 易过期） | **极高**（动态注入 Session） |
| **代码质量** | 脏乱（硬编码多） | **优异**（符合项目模板规范） |
| **维护成本** | 高（需手动重构所有逻辑） | **低**（AI 处理关联与参数化） |
| **学习成本** | 需学习录制框架 | **零成本**（只要会点点点 + cURL） |

---

## ⚠️ 治理规则

1. **临时性**：`api_record/raw_curls/` 下的文件不合入 Git 主干，完成代码生成后应立即删除。
2. **脱敏录制**：录制器已自动剔除 `Cookie` 和 `Authorization`，严禁在录制配置中手动开启敏感 Header 采集。
3. **人工核对**：AI 生成的代码虽然符合模板，但业务逻辑（如断言的业务字段）仍需人工进行最终 Check。

---

**下一步建议：**
你想让我帮你写一个完整的 `start_recorder.py` 启动脚本吗？它可以自动帮你处理虚拟环境和 mitmproxy 证书检查。