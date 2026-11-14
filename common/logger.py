"""日志工具：控制台 + 按天切分的文件日志。

所有模块的 logger 共用一个 handler 组（挂在包级 logger 上），
避免每个业务 logger 各自打开一份文件句柄导致重复写盘。
日志级别取自 config/config.yaml 的 log.level。
"""
import logging
import os
from datetime import datetime

from config.read_config import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 包级 logger 名称，业务 logger 都是它的子 logger（pytest_project.api 等）
ROOT_LOGGER_NAME = "pytest_project"
_configured = False


def _configure_root():
    """只初始化一次：控制台 + 当天日志文件"""
    global _configured
    if _configured:
        return

    root_logger = logging.getLogger(ROOT_LOGGER_NAME)
    root_logger.setLevel(_get_level())

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台输出
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root_logger.addHandler(console)

    # 文件输出：按天切分，文件名即日期
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root_logger.addHandler(file_handler)

    # 不再向 root 传播，避免第三方库/框架重复打印
    root_logger.propagate = False
    _configured = True


def _get_level():
    """从配置读取日志级别，非法值回退 INFO"""
    name = str(config.get("log", "level", default="INFO")).upper()
    return getattr(logging, name, logging.INFO)


def get_logger(name="test"):
    """获取带统一 handler 的业务 logger，如 get_logger("api")"""
    _configure_root()
    return logging.getLogger(f"{ROOT_LOGGER_NAME}.{name}")
