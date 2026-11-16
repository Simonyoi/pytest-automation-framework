"""Web UI 结算流程测试用例"""
import allure
import pytest

from config.read_config import config
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@allure.feature("Web UI-结算")
class TestCheckout:

    def _prepare_cart(self, driver):
        """前置：登录 → 加购 1 件 → 进入购物车页"""
        driver.get(config.get("web", "base_url"))
        acct = config.get("web", "account")
        LoginPage(driver).login(acct["username"], acct["password"])

        home = HomePage(driver)
        home.wait_url_contains("/inventory.html")
        home.add_first_item()
        home.go_cart()
        CartPage(driver).wait_loaded()

    @allure.story("结算主流程")
    @pytest.mark.smoke
    def test_checkout_success(self, driver):
        """加购 → 结算 → 填信息 → 看到总价 → 提交 → 完成页"""
        self._prepare_cart(driver)
        CartPage(driver).checkout()

        page = CheckoutPage(driver)
        page.fill_info("测试", "用户", "100000")
        page.continue_to_step_two()

        page.wait_step_two()
        total = page.get_total()
        assert total.startswith("Total:"), f"订单总价未显示: {total}"

        page.finish()
        header = page.get_complete_header()
        assert "Thank you for your order" in header, f"未进入订单完成页: {header}"

    @allure.story("结算必填校验")
    @pytest.mark.parametrize(
        "first_name, last_name, postal_code, expect_msg",
        [
            pytest.param("", "", "", "First Name is required", id="缺少姓名"),
            pytest.param("测试", "", "", "Last Name is required", id="缺少姓氏"),
            pytest.param("测试", "用户", "", "Postal Code is required", id="缺少邮编"),
        ],
    )
    def test_checkout_missing_field(self, driver, first_name, last_name, postal_code, expect_msg):
        """三个必填项分别缺失 → 应提示对应字段必填"""
        self._prepare_cart(driver)
        CartPage(driver).checkout()

        page = CheckoutPage(driver)
        page.wait_step_one()
        page.fill_info(first_name, last_name, postal_code)
        page.click(page.CONTINUE_BTN)

        error = page.get_error()
        assert expect_msg in error, f"未提示 {expect_msg}: {error}"