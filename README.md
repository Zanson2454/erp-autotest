# ERP 自动化测试项目

## 项目简介
本项目是一个基于 Python 的 ERP 系统自动化测试框架，主要用于测试销售订单相关的业务流程。

## 技术栈
- Python 3.x
- pytest
- Allure
- requests
- loguru

## 项目结构
```
erp-autoest/
├── config/                # 配置文件目录
├── docs/                  # 文档目录
├── reports/              # 测试报告目录
│   └── allure-results/   # Allure 报告数据
├── requirements/         # 依赖管理目录
│   ├── requirements.txt    # 生产环境依赖
│   ├── requirements-dev.txt # 开发环境依赖
│   └── requirements-test.txt # 测试环境依赖
├── testcases/           # 测试用例目录
│   └── SCM/            # 模块测试目录
│       └── SO/        # 销售订单测试目录
├── utils/              # 工具类目录
└── run_test.sh        # 测试执行脚本
```

## 环境准备
1. 安装 Python 3.x
2. 安装项目依赖：
   ```bash
   pip install -r requirements/requirements-test.txt
   ```
3. 安装 Allure：
   ```bash
   # macOS
   brew install allure
   
   # Windows
   scoop install allure
   ```

## 测试执行
1. 运行单个测试用例：
   ```bash
   pytest testcases/SCM/SO/test_01_create.py -v
   ```

2. 运行整个模块测试：
   ```bash
   pytest testcases/SCM/SO -v
   ```

3. 使用集成脚本运行测试并生成报告：
   ```bash
   ./run_test.sh
   ```

## 测试报告
- 测试执行完成后，会自动生成 Allure 报告
- 报告包含测试用例执行情况、错误信息、日志等详细信息
- 可以通过浏览器访问生成的报告链接查看详情

## 测试用例说明
### 销售订单创建测试
- 测试文件：`testcases/SCM/SO/test_01_create.py`
- 主要测试点：
  - 销售订单初始化
  - 客户信息查询
  - 相关方查询
  - 销售组织查询
  - 物料查询
  - 订单行渲染
  - 自动定价
  - 订单保存
  - 订单提交

## 日志记录
- 使用 loguru 进行日志记录
- 日志级别：DEBUG, INFO, WARNING, ERROR
- 日志文件位置：`logs/`

## 注意事项
1. 运行测试前确保环境配置正确
2. 检查配置文件中的接口地址是否正确
3. 确保测试数据准备充分
4. 注意测试用例之间的依赖关系

## 常见问题
1. 测试失败时，查看日志和报告获取详细信息
2. 检查网络连接和接口状态
3. 确认测试数据是否有效

## 贡献指南
1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 版本历史
- v1.0.0: 初始版本
  - 实现销售订单创建流程测试
  - 集成 Allure 报告
  - 添加日志记录功能 