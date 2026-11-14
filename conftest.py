"""根级 conftest：放置跨接口/Web 方向复用的全局 fixture。

fixture 分三层：
1. 根级 conftest.py（本文件）：全局通用
2. testcases/api/conftest.py：接口方向专用
3. testcases/web/conftest.py：Web UI 方向专用

logger fixture 被 Web 方向的 driver 等 fixture 消费，保证三层 fixture 是真实链路。
"""
import pytest

from common.logger import get_logger


@pytest.fixture(scope="session")
def logger():
    """全局日志对象，session 级别只初始化一次"""
    return get_logger("test")
