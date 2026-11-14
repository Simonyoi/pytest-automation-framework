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

    @allure.story("按价格从低到高排序")
    @pytest.mark.smoke
    def test_sort_price_asc(self, driver):
        self._login(driver)
        home = HomePage(driver)

        home.sort_by("lohi")
        prices = home.get_prices()

        assert prices, "商品列表为空，无法验证排序"
        assert prices == sorted(prices), f"价格未按升序排列: {prices}"