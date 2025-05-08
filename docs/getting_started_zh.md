# ERP自动化测试框架使用指南

## 环境要求

在开始之前，请确保您的系统已安装以下软件：
- Python 3.8 或更高版本
- pip (Python包管理器)
- Git

## 安装步骤

1. 克隆代码仓库：
```bash
git clone [仓库地址]
cd erp_autotest
```

2. 创建并激活虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Windows系统使用: venv\Scripts\activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 项目结构

```
erp_autotest/
├── docs/               # 文档文件
├── testcases/         # 测试用例和测试套件
│   ├── crm/          # CRM模块测试用例
│   ├── inv/          # 库存模块测试用例
│   ├── sls/          # 销售模块测试用例
│   ├── gen/          # 通用模块测试用例
│   └── comm/         # 公共组件测试用例
├── utils/             # 工具函数和辅助类
├── config/            # 配置文件
├── data/             # 测试数据文件
├── logs/             # 日志文件
├── reports/          # 测试报告
└── requirements.txt   # 项目依赖
```

## 编写第一个测试

1. 在 `testcases` 目录下创建新的测试文件：
```python
from utils.test_base import TestBase

class TestExample(TestBase):
    def test_login(self):
        # 在这里编写测试代码
        pass
```

2. 运行测试：
```bash
python -m pytest testcases/test_example.py -v
```

## 配置说明

1. 在 `.env` 文件中设置环境变量：
```
ERP_URL=您的ERP系统地址
USERNAME=您的用户名
PASSWORD=您的密码
```

2. 在 `config/test_config.yaml` 中配置测试参数：
```yaml
browser:
  name: chrome
  headless: true
timeout:
  implicit: 10
  explicit: 20
```

## 最佳实践

1. **测试组织**
   - 将相关测试组织在测试类中
   - 使用描述性的测试名称
   - 遵循 Arrange-Act-Assert（准备-执行-断言）模式
   - 按模块分类组织测试用例（如CRM、库存、销售等）

2. **数据管理**
   - 使用测试夹具（fixtures）进行通用设置
   - 将测试数据与测试逻辑分离
   - 测试完成后清理测试数据
   - 将测试数据文件存放在 `data` 目录下

3. **错误处理**
   - 添加适当的错误信息
   - 在适当的地方使用 try-except 块
   - 记录测试执行详情到 `logs` 目录

## 运行测试

### 运行所有测试：
```bash
pytest
```

### 运行特定模块的测试：
```bash
pytest testcases/crm/  # 运行CRM模块测试
pytest testcases/inv/  # 运行库存模块测试
```

### 运行特定测试文件：
```bash
pytest testcases/test_example.py
```

### 运行带有特定标记的测试：
```bash
pytest -m smoke
```

### 生成测试报告：
```bash
pytest --html=reports/report.html
```

## 常见问题解决

常见问题及解决方案：

1. **连接问题**
   - 确认ERP系统可访问
   - 检查网络连接
   - 验证登录凭据

2. **测试失败**
   - 检查测试日志（logs目录）
   - 验证测试数据
   - 确保环境配置正确

## 参与贡献

1. Fork 项目仓库
2. 创建特性分支
3. 提交您的更改
4. 推送到分支
5. 创建 Pull Request

## 获取帮助

如需帮助：
- 查看文档
- 在仓库中提交问题
- 联系开发团队

## 许可证

[许可证信息] 