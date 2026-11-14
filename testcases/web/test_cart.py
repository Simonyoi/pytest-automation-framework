"""Web UI 购物车测试用例"""
import allure
import pytest

from config.read_config import config
from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@allure.feature("Web UI-购物车")
class TestCart:

    def _login(self, driver):
        driver.get(config.get("web", "base_url"))
        acct = config.get("web", "account")
        LoginPage(driver).login(acct["username"], acct["password"])
        HomePage(driver).wait_url_contains("/inventory.html")

    @allure.story("添加商品到购物车")
    @pytest.mark.smoke
    def test_add_to_cart(self, driver):
        self._login(driver)
        home = HomePage(driver)
        before = home.item_count()
        assert before > 0, "商品列表为空"

        home.add_first_item()
        # 先校验购物车角标，确认加购动作生效，再进购物车页统计
        assert home.get_cart_badge() == "1", "购物车角标未更新为 1"

        home.go_cart()
        assert CartPage(driver).item_count() == 1, "购物车内商品数量不为 1"

    @allure.story("从购物车移除商品")
    def test_remove_from_cart(self, driver):
        """加购 1 件 → 进购物车 → 移除 → 购物车应为空"""
        self._login(driver)

        home = HomePage(driver)
        home.add_first_item()
        assert home.get_cart_badge() == "1", "购物车角标未更新为 1"

        home.go_cart()
        cart = CartPage(driver)
        assert cart.item_count() == 1, "购物车应有 1 件商品"

        cart.remove_first_item()
        assert cart.item_count() == 0, "移除后购物车仍有商品"

    @allure.story("多商品加购角标累加")
    def test_add_multiple_items(self, driver):
        """加购 2 件 → 角标依次变 1、2 → 购物车里有 2 件"""
        self._login(driver)
        home = HomePage(driver)

        home.add_item_by_index(0)
        home.wait_text(HomePage.CART_BADGE, "1")

        home.add_item_by_index(1)
        home.wait_text(HomePage.CART_BADGE, "2")

        home.go_cart()
        assert CartPage(driver).item_count() == 2, "购物车内商品数量不为 2"