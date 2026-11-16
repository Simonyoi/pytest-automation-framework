"""Web UI 权限校验用例：未登录不能直接进入受保护页面。

driver fixture 已经打开过首页并清空登录态，这里直接拼受保护页地址，
验证前端路由守卫会把人踢回登录页并给出提示，而不是渲染出商品列表。
"""
import allure
import pytest

from config.read_config import config
from pages.login_page import LoginPage


@allure.feature("Web UI-权限校验")
class TestWebAuthGuard:

    @allure.story("未登录直接访问商品列表被拦截")
    @pytest.mark.regression
    def test_inventory_requires_login(self, driver):
        base_url = config.get("web", "base_url")
        driver.get(f"{base_url}/inventory.html")

        page = LoginPage(driver)
        # 等登录按钮出现：若被重定向，说明守卫生效；超时说明页面没回到登录页
        page.wait_visible(page.LOGIN_BTN)

        assert "inventory" not in driver.current_url, (
            f"未登录仍停留在受保护页面: {driver.current_url}"
        )

        error = page.get_error()
        assert "logged in" in error.lower(), f"未提示需要登录: {error}"
