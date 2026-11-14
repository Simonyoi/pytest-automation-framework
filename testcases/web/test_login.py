"""Web UI 登录测试用例（数据驱动）"""
import allure
import pytest

from common.read_data import get_test_data
from config.read_config import config
from pages.home_page import HomePage
from pages.login_page import LoginPage

cases = get_test_data("web/login_data.yaml")["login_cases"]


@allure.feature("Web UI-登录")
class TestLogin:

    @allure.story("登录")
    @pytest.mark.parametrize("case", cases, ids=[c["name"] for c in cases])
    def test_login(self, driver, case):
        driver.get(config.get("web", "base_url"))
        page = LoginPage(driver)
        page.login(case["username"], case["password"])

        if case["expect"] == "success":
            home = HomePage(driver)
            home.wait_url_contains("/inventory.html")
            assert home.get_title() == "Products", "登录成功但未进入商品列表页"
        else:
            error = page.get_error()
            assert "Epic sadface" in error, f"未出现登录错误提示: {error}"
