# Pytest 自动化测试框架（接口 + Web UI 双方向）

[![自动化测试 CI](https://github.com/Simonyoi/pytest-automation-framework/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Simonyoi/pytest-automation-framework/actions/workflows/ci.yml)

基于 **Pytest + Selenium + Requests + Allure** 搭建的自动化测试框架，采用分层架构（数据层 / 服务层与页面对象层 / 用例层），覆盖**接口自动化**和 **Web UI 自动化**两个方向。

## 技术栈

| 类别 | 技术 |
|------|------|
| 测试框架 | Pytest（fixture、parametrize 数据驱动、markers） |
| 接口自动化 | Requests（BaseApi 请求基类 + 服务层，可选 x-api-key 鉴权） |
| Web UI 自动化 | Selenium WebDriver + Page Object Model（POM） |
| 报告 | Allure + pytest-html（每次运行自动清理历史结果） |
| 配置/数据 | YAML（config.yaml + data/ 测试数据） |
| 日志 | logging（控制台 + 按天切分文件，级别由 config 控制） |
| 容错 | 失败自动截图（setup/call）、显式等待、异常重试、5xx 退避重试 |
| 依赖 | requirements.txt 锁定为已验证版本组合 |

## 被测对象

| 方向 | 目标 | 说明 |
|------|------|------|
| 接口 | https://reqres.in/api | 免费仿真 REST API（登录/注册鉴权 + 用户 CRUD + 分页） |
| Web UI | https://www.saucedemo.com | 电商测试站（登录 → 商品列表 → 购物车 → 结算） |

## 架构设计

```
pytest_project/
├── conftest.py               # 根级 fixture（全局通用）
├── pytest.ini                # pytest 配置
├── requirements.txt          # 依赖清单
├── config/                   # 配置层
│   ├── config.yaml           #   环境/浏览器/账号/超时等
│   └── read_config.py        #   配置读取单例
├── common/                   # 公共层（底座）
│   ├── base_api.py           #   接口请求基类（重试/鉴权/日志）
│   ├── base_page.py          #   Web 页面基类（含显式等待）
│   ├── logger.py             #   日志
│   └── read_data.py          #   读取 yaml 测试数据
├── api/                      # 接口服务层（类比 POM）
│   ├── login_api.py          #   登录/注册
│   └── user_api.py           #   用户 CRUD
├── pages/                    # Web 页面对象层（POM）
│   ├── login_page.py
│   ├── home_page.py          #   商品列表页
│   ├── cart_page.py
│   └── checkout_page.py      #   结算流程（覆盖三个子页面）
├── testcases/                # 用例层（只写测试逻辑 + 断言）
│   ├── __init__.py           #   包标记，避免同名用例文件 import 冲突
│   ├── api/
│   │   ├── __init__.py
│   │   ├── conftest.py       #   配置/服务层 fixture + 数据集探测
│   │   ├── test_login_api.py
│   │   ├── test_register_api.py
│   │   └── test_user_crud.py
│   └── web/
│       ├── __init__.py
│       ├── conftest.py       #   driver fixture + 失败截图（setup/call）
│       ├── test_login.py
│       ├── test_inventory.py
│       ├── test_cart.py
│       └── test_checkout.py
├── data/                     # 数据层（与代码分离）
│   ├── api/
│   │   ├── login_data.yaml
│   │   └── register_data.yaml
│   └── web/login_data.yaml
├── .cache/                   # 驱动缓存 / 浏览器 profile / 临时目录（已 gitignore）
├── logs/                     # 运行日志（按天切分）
├── reports/                  # 测试报告（html + allure_results）
└── screenshots/              # Web 失败截图（仅失败时生成）
```

**核心思想：三层分离** —— 数据(`data`) / 服务与页面(`api`+`pages`) / 用例(`testcases`) 互不耦合。改元素只改 `pages`，改用例只改 `testcases`，改数据只改 `data`。

**fixture 作用域约定**：配置类用 `session`（只读一次）；服务层实例与 `driver` 用 `function`（用例互不污染，用完显式 `close()`/`quit()`）；`user_dataset` 用 `session`（数据集只探测一次，供用例动态推导 id）。

## 环境准备

1. Python 3.10+（本机验证：3.11.5）
2. 浏览器：Chrome 或 Edge（默认 Edge，可在 `config/config.yaml` 的 `web.browser` 切换）
3. 创建虚拟环境并安装依赖：

```bash
# Windows（不要加 --system-site-packages，否则依赖会从系统 Python 解析）
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 说明：Selenium 4.6+ 会通过 Selenium Manager 自动下载与浏览器版本匹配的 driver，无需手动下载 chromedriver/msedgedriver。本项目已将 driver 缓存（`.cache/selenium`）、浏览器 profile（`.cache/browser_profile`）和浏览器临时目录（`.cache/tmp`）全部指向项目内，避开设用户目录/`%TEMP%` 时的权限问题；本次运行结束后会自动清理 profile。

## 接口配额与 API Key（可选）

reqres.in 匿名 demo **按 IP 限流 40 次/天**，本套用例单次全量约消耗 19 次请求，反复运行会触发 429；注册免费账号（约 **250 次/天**）并注入 key 可缓解。任选一种方式：

```powershell
# 方式一：环境变量（推荐，key 不进 git）
$env:REQRES_API_KEY = "你的key"
```

```yaml
# 方式二：填入 config/config.yaml（该文件被 git 跟踪，切勿提交真实 key）
api:
  api_key: "你的key"
```

读取优先级：`REQRES_API_KEY` 环境变量 > `config.yaml` 的 `api.api_key`；生效后 `BaseApi` 自动附加 `x-api-key` 请求头。

## 运行测试

```bash
# 跑全部用例
pytest

# 只跑接口方向
pytest testcases/api

# 只跑 Web UI 方向
pytest testcases/web

# 冒烟测试（登录/列表/创建/加购/结算/排序 6 条主链路，展开为 9 个用例）
pytest -m smoke

# 并行执行（仅建议用于接口方向；Web 方向会同时开多个浏览器）
pytest testcases/api -n auto
```

## 测试报告

### 方式一：pytest-html

运行后自动生成 `reports/html/report.html`，浏览器直接打开。

### 方式二：Allure

1. 安装 Allure 命令行工具（见 https://allurereport.org/docs/install/ ）
2. 运行测试（会自动生成 allure 结果到 `reports/allure_results`；`--clean-alluredir` 会先清空历史结果，避免报告混入旧用例）
3. 生成并查看报告：

```bash
allure generate reports/allure_results -o reports/allure_report --clean
allure open reports/allure_report
```

## 测试覆盖

共 **25 条**用例（接口 16 + Web 9）。

**接口方向（reqres.in）**
- 登录：成功 / 缺少密码 / 用户不存在（数据驱动，3 条）
- 注册：成功 / 缺少密码（数据驱动，2 条）
- 用户 CRUD：列表分页(第 1/2 页)、查询单个、查询不存在(404)、创建(201)、更新、删除(204)、分页元信息自洽、分页数据不重叠、用户字段完整性、响应头 Content-Type（11 条）
- 用例中的用户 id 由 `user_dataset` 探测到的数据集推导，数据规模变化时无需改代码

**Web UI 方向（saucedemo.com）**
- 登录：成功 / 密码错误 / 账号锁定（数据驱动，3 条）
- 商品列表：按价格升序排序（1 条）
- 购物车：加购（角标+数量校验） / 移除 / 多商品加购角标累加（3 条）
- 结算：主流程（填信息 → 确认总价 → 完成页） / 缺少姓名必填校验（2 条）

## 项目亮点

1. **POM + 服务层**：页面/接口操作与用例解耦，可维护性强
2. **数据驱动**：`pytest.mark.parametrize` + yaml 数据，一条用例跑多组数据
3. **三层 fixture**：根级 / 接口 / Web 分层管理，作用域按“配置 session、实例 function、数据集 session”约定
4. **工程化容错**：失败自动截图（setup/call 双阶段）、显式等待（替代 time.sleep）、异常重试、5xx 退避重试、日志落地
5. **可复现**：requirements 锁定已验证版本，`--clean-alluredir` 保证报告不串数据
6. **双报告**：Allure + pytest-html
7. **数据自洽**：用例 id 从被测数据集推导，不用魔法数字
8. **业务全链路**：Web 覆盖登录 → 商品列表（排序）→ 购物车（加购/移除）→ 结算（含必填校验）完整电商主流程

## 健壮性设计

| 场景 | 处理方式 |
|------|----------|
| 请求超时 / 连接中断 / 分块传输异常 | `BaseApi` 捕获 `requests.RequestException` 全族异常，按 `api.retries` 重试，仍失败则抛出并记录 error 日志 |
| 接口 5xx | 命中 500/502/503/504 时按 `backoff * n` 退避重试 |
| 接口限流（429） | 视为配额信号不重试，直接记录可操作的 error 日志（提示配置 `api.api_key`） |
| 接口配额不足 | 设置 `REQRES_API_KEY` 环境变量或填入 `config.yaml` 的 `api.api_key` 后自动附加 `x-api-key` 头（环境变量优先） |
| 页面元素未就绪 | 全部改为显式等待（`wait_visible` / `wait_present` / `wait_url_contains`），无 `time.sleep` |
| 页面跳转后立刻统计 | `CartPage.item_count()` 先等待 URL 与结算按钮，再统计元素 |
| 用例失败 | 自动截图落 `screenshots/` 并附加到 Allure，setup 阶段（如 driver 起不来）同样覆盖 |
| 用例互相污染 | 服务层实例与 driver 均为 function 作用域，用完显式 `close()` / `quit()` |
| 用例残留登录态/购物车数据 | driver fixture 每条用例先清空 localStorage / sessionStorage / cookie，保证从干净状态开始 |
| 报告数据串台 | `--clean-alluredir` 每次运行清空历史结果 |
| 受限 Windows 环境浏览器起不来 | 在 `testcases/web/conftest.py` 统一设置：项目内 driver 缓存 / 独立 profile / 项目内 TEMP / 标准 CI 启动参数（含 `--no-sandbox`） |

## 已知限制

- 接口依赖 reqres.in 公共 demo，**匿名配额仅 40 次/天**（按 IP 计）。本套用例单次全量约消耗 19 次请求，超配额会返回 429；注册免费账号（约 250 次/天）并设置 `REQRES_API_KEY` 环境变量可缓解，步骤见「接口配额与 API Key」。
- Web 方向依赖真实浏览器与网络：首次运行由 Selenium Manager 下载匹配驱动到 `.cache/selenium/`，**离线环境不可用**。
- reqres 的写接口（创建/更新/删除）不真正持久化数据，因此不做“写后读”一致性断言，只校验响应契约。

## 本机验证

验证环境：Windows 11 + Python 3.11.5 + pytest 9.2.0 + selenium 4.52.0 + Edge 126。

| 命令 | 结果 |
|------|------|
| `pytest testcases/api -q` | 16 passed（配额充足时，约 2-3 分钟，受 demo 限流影响） |
| `pytest testcases/web -q` | 9 passed（约 1 分钟） |
| `pytest -m smoke --collect-only -q` | 9/25 用例被选中（markers 生效） |
| `pytest -q` | 配额耗尽时后段用例会返回 429，需配置 `api_key` 后复跑 |
