"""登录接口测试用例（数据驱动）"""
import allure
import pytest

from common.read_data import get_test_data

cases = get_test_data("api/login_data.yaml")["login_cases"]

# 冒烟标记由数据层的 smoke 字段决定：只有主链路成功用例进冒烟集，
# 负向/边界数据不会因为函数级 marker 被一起拉进冒烟，避免冒烟集随数据增长而膨胀
PARAMS = [
    pytest.param(case, id=case["name"], marks=pytest.mark.smoke)
    if case.get("smoke")
    else pytest.param(case, id=case["name"])
    for case in cases
]


@allure.feature("接口-登录")
class TestLoginApi:

    @allure.story("登录")
    @pytest.mark.parametrize("case", PARAMS)
    def test_login(self, login_api, case):
        resp = login_api.login(case["email"], case["password"])
        assert resp.status_code == case["expect_code"], f"状态码错误: {resp.status_code}"
        body = resp.json()
        if case["expect_token"]:
            assert "token" in body, f"登录成功未返回 token: {body}"
        else:
            assert "error" in body, f"登录失败未返回 error: {body}"
