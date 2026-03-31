# Architecture Layers（当前实际）
```
1. 执行层      pytest.ini + testcases/conftest.py
               ├── env/project 注入
               ├── serial_flow 标记 + job-group 过滤
               └── pytest_sessionfinish → cleanup_registry.run_cleanups()

2. 编排层      模块基类（继承 BaseTest） + 业务用例
               └── 子类 teardown_class → __init_subclass__ 强制兜底 super()

3. 调用层      BaseTest.standard_api_call
               └── ApiCallService.execute()
                   ├── ApiClientFacade（路径解析 + 近似匹配）
                   ├── ParamUtil（payload 过滤/注入）
                   └── HttpUtil（GET/POST/PUT/DELETE/PATCH）

4. 上下文层    AuthContext（认证VO）
               TestDataContext（缓存路径解析）
               bind_cache_data()（默认14字段快速绑定）

5. 数据层      DataFactory → init_data / md_cache_data
               DBManager（erp_db / iam_db 双连接）
               CacheUtil（JSON持久化缓存）

6. 清理层      cleanup_registry（注册式，session末尾单点执行）
               + 模块 teardown_class（存量，逐步迁移中）
```

# Directory Structure
```
testcases/
├── conftest.py                   # 全局 hook：排序、分组、统一清理触发
├── comm/
│   ├── base_test.py              # 核心基类 (1179 行，含 ConfigManager/SessionManager/LoginService/BaseTestInitializer/BaseTest)
│   ├── api_call_service.py       # standard_api_call 执行层 (182 行)
│   ├── api_client_facade.py      # API 路径解析门面
│   ├── auth_context.py           # 认证上下文 VO
│   ├── test_data_context.py      # 缓存路径解析
│   └── cleanup_registry.py       # 清理注册中心
├── gen_md/
│   ├── conftest.py               # 注册式清理（230 行，30+ 张表，含动态列探测）
│   └── {gen_base,org,mat,partner,todo}/
├── erp_fin/
│   ├── conftest.py               # 已有 conftest（迁移状态待确认）
│   └── {fin_iv,fin_ap,...}/
├── scm_sls/
│   ├── conftest.py               # 注册式清理
│   └── {cf,md,so_0x,...}/
├── scm_del/
│   ├── conftest.py               # 注册式清理
│   └── ...
└── {scm_pur,scm_inv,sys_common,...}/  # 25 个模块，清理模式待迁移
```

# Module Responsibilities
| 组件 | 职责 | 说明 |
|---|---|---|
| `ConfigManager` | 配置加载/缓存/校验 | 支持多项目隔离，mask 敏感字段 |
| `SessionManager` | HTTP 会话管理 | 多进程按 PID 隔离 session |
| `LoginService` | 登录/认证/占位符检测 | 支持多门户 |
| `BaseTestInitializer` | 初始化编排（5步模板） | 分离 BaseTest 初始化细节 |
| `BaseTest` | 测试基类：setup 编排 + 公共 API 调用入口 | 仍是主承载点，1179 行 |
| `ApiCallService` | standard_api_call 执行 | 依赖 test_obj，耦合测试上下文 |
| `ApiClientFacade` | API 路径解析 + 近似匹配 | 有 warning 日志 |
| `AuthContext` | 认证输出 VO | 纯数据结构 |
| `TestDataContext` | 缓存路径解析 | 支持 init_data / md_cache_data 两个数据源 |
| `cleanup_registry` | 全局清理注册中心 | order 参数控制执行顺序，幂等，支持 reset |

# Request Lifecycle（完整调用链）
```
test method
  └─▶ self.standard_api_call(api_key, set_dict, ...)
        └─▶ ApiCallService.execute(test_obj, api_key, ...)
              ├─▶ test_obj.get_api_path(api_key)
              │     └─▶ ApiClientFacade.resolve_api_path(apis_dict, api_key)
              │           └─▶ ParamUtil.get_api_path(...)
              ├─▶ test_obj.get_api_params(api_path)
              │     └─▶ ApiClientFacade.resolve_api_params(...)
              │           └─▶ ParamUtil.get_api_params(...)
              ├─▶ ParamUtil.filter_post_body_fields(...)
              ├─▶ ParamUtil.set_request_params(...)
              ├─▶ ParamUtil.sanitize_payload(...)
              ├─▶ assert_util.set_request_context(...)
              └─▶ test_obj.http.post/get/put/delete(url, ...)
                    └─▶ HttpUtil → requests.Session
```

# Fixture Dependency
```
testcases/conftest.py (session 级)
  ├── pytest_collection_modifyitems → 排序 + serial_flow + job-group 过滤
  ├── pytest_sessionfinish → cleanup_registry.run_cleanups() (主进程)
  └── allure 集成 hook

模块 conftest (模块级)
  ├── gen_md/conftest.py → register_cleanup("gen_md_cleanup", ..., order=250)
  ├── scm_sls/conftest.py → 注册式（已迁移）
  └── scm_del/conftest.py → 注册式（已迁移）

BaseTest.__init_subclass__
  └── 装饰子类 teardown_class，finally 兜底调用 BaseTest.teardown_class
```

# Config Flow
```
1. CLI: --env=test --project=xxx → os.environ
2. DataFactory(env_name, project).get_env_config()
   └── config/env/{project}/{env}.yaml
3. ConfigManager: merge + validate + cache
4. BaseTestInitializer.initialize_environment()
5. LoginService.login(portal_key, tenant_key)
   └── POST /iam/api/v1/user/login/account
   └── GET  /api/trantor/portal/user/current
6. DBManager(erp_db / iam_db)
7. BaseTest 各属性挂载完毕
```

# Test Data Lifecycle
```
1. 初始化
   DataFactory.init_sql_cache() → CacheUtil.set("md_init_cache", ...)
   BaseTest._initialize_data() → init_data

2. 绑定
   cls.bind_cache_data() → TestDataContext.resolve_cache_path()
   → 支持 "currency_info.curr_id" / "partner_info.cust_info.id" 等点分路径

3. 执行
   test_method → standard_api_call → AT_ 前缀数据写入 DB

4. 清理（双轨并存）
   - 注册式：pytest_sessionfinish → cleanup_registry.run_cleanups()
   - 分散式：teardown_class → cls.db.delete(...)
```

# Assertion Layer
```
Level 1: assert_util.assert_response_success(response)   # HTTP + success字段
Level 2: assert_util.assert_response_data(response)      # data非空
Level 3: assert_util.assert_by_operator(actual, op, expected)  # 字段级
Level 4: self.db.query_one(sql, params)                  # DB状态验证
```

# How to Add New Module（规范步骤）
```
1. 建配置
   testdata/{module}/{module}_api_path.yaml
   testdata/{module}/{module}_api_params.yaml

2. 建基类
   testcases/{module}/__init__.py
   class {Module}BaseTest(BaseTest):
       @classmethod
       def setup_class(cls):
           super().setup_class()
           cls.load_module_api_configs(path_file, params_file)
           cls.bind_module_user_context("{module}")
           cls.bind_cache_data()     # 绑定常用数据
           cls.bind_mock_util_singleton()

3. 建清理
   testcases/{module}/conftest.py
   register_cleanup("{module}_cleanup", _cleanup_func, order=xxx)
   # 不要在 teardown_class 写新的分散清理

4. 建用例
   testcases/{module}/test_{feature}_management.py
   class Test{Feature}Management({Module}BaseTest):
       # file_level_order 控制串行顺序
       # try-except + a.text(str(e), "失败原因")
       # 3层断言
```
