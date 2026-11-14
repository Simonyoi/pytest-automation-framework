"""注册接口测试用例（数据驱动）"""
import allure
import pytest

from common.read_data import get_test_data

cases = get_test_data("api/register_data.yaml")["register_cases"]


@allure.feature("接口-注册")
class TestRegisterApi:

    @allure.story("注册")
    @pytest.mark.parametrize("case", cases, ids=[c["name"] for c in cases])
    def test_register(self, login_api, case):
        resp = login_api.register(case["email"], case["password"])
        assert resp.status_code == case["expect_code"], f"状态码错误: {resp.status_code} {resp.text[:200]}"

        body = resp.json()
        if case["expect_token"]:
            assert body.get("id"), f"注册成功未返回 id: {body}"
            assert body.get("token"), f"注册成功未返回 token: {body}"
        else:
            assert "error" in body, f"注册失败未返回 error: {body}"