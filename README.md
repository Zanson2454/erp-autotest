# API 自动化测试框架

基于 Requests + Pytest + Allure 的 API 自动化测试框架。

## 功能特点

- 支持多环境配置（dev/test/prod）
- 封装了常用的 HTTP 请求方法
- 集成了 Allure 报告
- 支持测试用例重试
- 支持并行执行测试
- 提供了丰富的断言方法

## 环境要求

- Python 3.8+
- pip

## 安装依赖

```bash
pip install -r requirements.txt
```

## 目录结构

```
├── tests/
│   ├── api/                # API 测试用例
│   ├── common/             # 公共组件
│   ├── config/             # 配置文件
│   ├── data/              # 测试数据
│   └── conftest.py        # pytest 配置文件
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明
```

## 运行测试

1. 运行所有测试：
```bash
pytest tests/
```

2. 指定环境运行：
```bash
pytest tests/ --env=test
```

3. 生成 Allure 报告：
```bash
pytest tests/ --alluredir=./reports
allure serve ./reports
```

4. 并行执行测试：
```bash
pytest tests/ -n auto
```

## 编写测试用例

1. 继承 BaseTest 类
2. 使用 Allure 装饰器添加测试信息
3. 使用封装的 HTTP 客户端发送请求
4. 使用断言方法验证响应

示例：
```python
@allure.epic("示例测试")
@allure.feature("用户管理")
class TestUser(BaseTest):
    @allure.story("用户登录")
    @allure.title("登录成功")
    def test_login_success(self):
        response = self.http_client.post("/api/login", json={
            "username": "test",
            "password": "123456"
        })
        self.assert_status_code(response, 200)
```

## 配置说明

1. 环境配置在 `tests/config/config.py` 中管理
2. 可以通过环境变量 `TEST_ENV` 指定测试环境
3. 也可以通过命令行参数 `--env` 指定测试环境

## 注意事项

1. 测试用例命名要以 `test_` 开头
2. 测试类命名要以 `Test` 开头
3. 建议使用 Allure 装饰器添加测试信息
4. 注意处理测试数据的清理 