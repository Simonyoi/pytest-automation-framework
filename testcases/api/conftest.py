"""接口方向专用 fixture：配置、服务层实例、数据集探测。

设计要点：
1. 配置类 fixture 用 session 作用域，一份配置只读一次；
2. 服务层实例用 function 作用域，用例之间 session/cookie 互不污染；
3. 数据集探测用 session 作用域，只额外请求一次，供用例动态推导 id，避免硬编码。
"""
import os

import pytest

from api.login_api import LoginApi
from api.user_api import UserApi
from config.read_config import config


@pytest.fixture(scope="session")
def api_base_url():
    return config.get("api", "base_url")


@pytest.fixture(scope="session")
def api_timeout():
    return config.get("api", "timeout", default=10)


@pytest.fixture(scope="session")
def api_retries():
    return config.get("api", "retries", default=0)


@pytest.fixture(scope="session")
def api_backoff():
    return config.get("api", "backoff", default=1)


# reqres 免费 key 的环境变量名：优先读环境变量，避免密钥落进 git
API_KEY_ENV = "REQRES_API_KEY"


@pytest.fixture(scope="session")
def api_key():
    # 环境变量优先，其次读 config.yaml；都为空则返回 None，BaseApi 不加鉴权头
    return os.getenv(API_KEY_ENV, "").strip() or config.get("api", "api_key", default="") or None


@pytest.fixture()
def login_api(api_base_url, api_timeout, api_retries, api_backoff, api_key):
    api = LoginApi(api_base_url, timeout=api_timeout, retries=api_retries,
                   backoff=api_backoff, api_key=api_key)
    yield api
    api.close()


@pytest.fixture()
def user_api(api_base_url, api_timeout, api_retries, api_backoff, api_key):
    api = UserApi(api_base_url, timeout=api_timeout, retries=api_retries,
                  backoff=api_backoff, api_key=api_key)
    yield api
    api.close()


@pytest.fixture(scope="session")
def user_dataset(api_base_url, api_timeout, api_retries, api_backoff, api_key):
    """拉取一次用户列表，作为"数据集事实"供其他用例推导 id/总数。

    这样被测服务的数据规模变化时，用例不需要改代码。
    """
    api = UserApi(api_base_url, timeout=api_timeout, retries=api_retries,
                  backoff=api_backoff, api_key=api_key)
    try:
        resp = api.list_users(1)
        assert resp.status_code == 200, f"前置数据拉取失败: {resp.status_code} {resp.text[:200]}"
        body = resp.json()
        assert body.get("data"), "前置数据拉取失败: 用户列表为空"
        return body
    finally:
        api.close()
