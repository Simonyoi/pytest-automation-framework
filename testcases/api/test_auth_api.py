"""接口鉴权用例：无效 api-key 必须被服务端拒绝。

与 5xx 重试策略的区别：鉴权失败是确定性结果，重试只会放大无效请求，
所以这里用 retries=0 的独立客户端，断言一次即定。
"""
import allure
import pytest

from api.user_api import UserApi


@pytest.fixture()
def invalid_key_api(api_base_url, api_timeout):
    """持有无效 api-key 的客户端，用完显式释放连接池"""
    api = UserApi(
        api_base_url,
        timeout=api_timeout,
        retries=0,
        backoff=0,
        api_key="invalid-key-for-auth-test",
    )
    yield api
    api.close()


@allure.feature("接口-鉴权")
class TestAuthGuard:

    @allure.story("无效 api-key 被拒绝")
    @pytest.mark.regression
    def test_invalid_api_key_rejected(self, invalid_key_api):
        """带无效 key 请求用户列表，应返回 403 且给出 invalid_api_key，而不是放行。

        实测 reqres 对"无效/已吊销的 key"返回 403（错误码 invalid_api_key），
        而不是 401（401 留给需要认证但未携带凭证的场景），断言按真实契约写。
        """
        resp = invalid_key_api.list_users(1)

        assert resp.status_code == 403, (
            f"无效 api-key 未被拒绝: {resp.status_code} {resp.text[:200]}"
        )
        body = resp.json()
        assert body.get("error") == "invalid_api_key", (
            f"拒绝原因不是 invalid_api_key: {body}"
        )
