"""购物车页页面对象"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class CartPage(BasePage):
    ITEM = (By.CLASS_NAME, "cart_item")
    CHECKOUT_BTN = (By.ID, "checkout")
    REMOVE_BTN = (By.CSS_SELECTOR, ".cart_item button")

    def wait_loaded(self):
        """等待购物车页渲染完成（结算按钮出现即视为就绪）"""
        self.wait_url_contains("/cart.html")
        return self.wait_present(self.CHECKOUT_BTN)

    def item_count(self):
        """先等页面就绪再统计，避免点击购物车图标后立即统计的竞态"""
        self.wait_loaded()
        return self.count(self.ITEM)

    def checkout(self):
        self.click(self.CHECKOUT_BTN)

    def remove_first_item(self):
        """移除购物车里的第一个商品，并等待它从列表消失"""
        self.wait_loaded()
        before = self.count(self.ITEM)
        self.click(self.REMOVE_BTN)
        self.wait_count(self.ITEM,before -1)
        return before - 1

