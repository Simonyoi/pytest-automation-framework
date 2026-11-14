"""Web UI 方向专用 fixture：driver 启动/关闭 + 失败自动截图。

driver 为 function 作用域：每个用例独立浏览器实例，互不污染。
失败截图覆盖 setup（如 driver 启动失败）与 call（断言/元素失败）两个阶段。
"""
import os
import shutil

import allure
import pytest
from selenium import webdriver

from config.read_config import config
from common.logger import get_logger

logger = get_logger("web")

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Selenium Manager 的驱动缓存目录改到项目内，避免写用户目录被权限拦截
os.environ.setdefault("SE_CACHE_PATH", os.path.join(BASE_DIR, ".cache", "selenium"))

# 浏览器用户数据目录也放项目内：部分 Windows 环境下 Edge/Chrome 无法在 %TEMP% 创建
# 临时用户数据目录，会报 SessionNotCreatedException: cannot create temp dir for user data dir
PROFILE_ROOT = os.path.join(BASE_DIR, ".cache", "browser_profile")

# 浏览器解压扩展/缓存所需的临时目录同样指向项目内，规避 %TEMP% 不可写的问题
# （否则报 cannot create temp dir for unpacking extensions）
TEMP_ROOT = os.path.join(BASE_DIR, ".cache", "tmp")
os.makedirs(TEMP_ROOT, exist_ok=True)
os.environ["TEMP"] = TEMP_ROOT
os.environ["TMP"] = TEMP_ROOT


# 浏览器启动参数：关闭首次运行引导/后台服务与组件更新，
# 否则在受限 Windows 环境下浏览器启动很慢，容易触发
# SessionNotCreatedException: unable to discover open pages
BROWSER_ARGS = [
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-extensions",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-component-update",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    # 受限环境下浏览器沙箱无法创建临时目录，会导致会话创建失败
    "--no-sandbox",
]


def _build_options(browser, headless):
    """构造浏览器选项：无头/窗口尺寸/独立用户数据目录/稳定性参数"""
    options = webdriver.ChromeOptions() if browser == "chrome" else webdriver.EdgeOptions()
    for arg in BROWSER_ARGS:
        options.add_argument(arg)
    if headless:
        options.add_argument("--headless=new")
        # 无头模式下 maximize_window 无效，显式指定窗口尺寸
        options.add_argument("--window-size=1920,1080")
    # 每次运行使用独立 profile，避免污染本机浏览器配置及并行时的目录互斥
    profile_dir = os.path.join(PROFILE_ROOT, f"{browser}-{os.getpid()}")
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")
    return options


@pytest.fixture(scope="session", autouse=True)
def _cleanup_browser_profile():
    """本次进程的浏览器 profile 在用例全部结束后清理，避免磁盘堆积"""
    yield
    for name in ("chrome", "edge"):
        shutil.rmtree(os.path.join(PROFILE_ROOT, f"{name}-{os.getpid()}"), ignore_errors=True)


@pytest.fixture(scope="function")
def driver(logger):
    browser = config.get("web", "browser", default="edge").lower()
    headless = config.get("web", "headless", default=False)
    logger.info("启动浏览器 browser=%s headless=%s", browser, headless)

    options = _build_options(browser, headless)
    drv = webdriver.Chrome(options=options) if browser == "chrome" else webdriver.Edge(options=options)

    try:
        if not headless:
            drv.maximize_window()

            # 每条用例都从干净状态开始：清掉上一条用例留在同一个 profile 里的购物车/登录态
            drv.get(config.get("web", "base_url"))
            drv.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
            drv.delete_all_cookies()
            
        yield drv
    finally:
        drv.quit()
        logger.info("浏览器已关闭")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图并附加到 Allure 报告（setup/call 阶段均覆盖）"""
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return

    funcargs = getattr(item, "funcargs", None) or {}
    drv = funcargs.get("driver")
    if drv is None:
        return

    shot_dir = os.path.join(BASE_DIR, "screenshots")
    path = os.path.join(shot_dir, f"{item.name}.png")
    try:
        os.makedirs(shot_dir, exist_ok=True)
        drv.save_screenshot(path)
        allure.attach.file(path, name="失败截图", attachment_type=allure.attachment_type.PNG)
        logger.info("失败截图已保存: %s", path)
    except Exception as e:
        # 截图属于辅助信息，失败不应影响用例结果，但要留下排查线索
        logger.warning("失败截图保存失败: %s", e)


