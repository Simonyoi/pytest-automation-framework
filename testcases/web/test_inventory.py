"""Web UI 商品列表测试用例"""
import allure
import pytest

from config.read_config import config
from pages.home_page import HomePage
from pages.login_page import LoginPage


@allure.feature("Web UI-商品列表")
class TestInventory:

    def _login(self, driver):
        """登录并停在商品列表页"""
        driver.get(config.get("web", "base_url"))
        acct = config.get("web", "account")
        LoginPage(driver).login(acct["username"], acct["password"])
        HomePage(driver).wait_url_contains("/inventory.html")

    @allure.story("商品排序")
    @pytest.mark.parametrize(
        "sort_value, expect",
        [
            pytest.param("lohi", "price_asc", id="价格升序", marks=pytest.mark.smoke),
            pytest.param("hilo", "price_desc", id="价格降序"),
            pytest.param("az", "name_asc", id="名称升序"),
            pytest.param("za", "name_desc", id="名称降序"),
        ],
    )
    def test_sort(self, driver, sort_value, expect):
        """四个排序方向分别校验：价格升/降、名称升/降"""
        self._login(driver)
        home = HomePage(driver)
        home.sort_by(sort_value)

        if expect.startswith("price"):
            values = home.get_prices()
            assert values, "商品列表为空，无法验证排序"
            expected = sorted(values) if expect == "price_asc" else sorted(values, reverse=True)
            label = "价格"
        else:
            values = home.get_names()
            assert values, "商品列表为空，无法验证排序"
            expected = sorted(values) if expect == "name_asc" else sorted(values, reverse=True)
            label = "名称"

        assert values == expected, f"{label}排序不符({expect}): {values}"
