"""商品列表页(登录后首页)页面对象"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class HomePage(BasePage):
    TITLE = (By.CLASS_NAME, "title")
    INVENTORY_ITEM = (By.CSS_SELECTOR, ".inventory_item")
    FIRST_ADD_BTN = (By.CSS_SELECTOR, ".inventory_item button")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    SORT_SELECT = (By.CSS_SELECTOR, "[data-test='product-sort-container']")
    ITEM_NAME = (By.CSS_SELECTOR, ".inventory_item_name")
    ITEM_PRICE = (By.CSS_SELECTOR, ".inventory_item_price")
    ADD_BTNS = (By.CSS_SELECTOR, ".inventory_item button")  # 所有商品的操作按钮


    def wait_loaded(self):
        """等待商品列表渲染完成"""
        return self.wait_present(self.INVENTORY_ITEM)

    def get_title(self):
        return self.get_text(self.TITLE)

    def item_count(self):
        self.wait_loaded()
        return self.count(self.INVENTORY_ITEM)

    def add_first_item(self):
        """添加第一个商品，并等待购物车角标更新"""
        self.wait_loaded()
        self.click(self.FIRST_ADD_BTN)
        self.wait_visible(self.CART_BADGE)

    def get_cart_badge(self):
        """购物车角标数量（字符串），未加购时不存在该元素"""
        return self.get_text(self.CART_BADGE)

    def go_cart(self):
        self.click(self.CART_LINK)

    def sort_by(self, value):
        """排序：az 名称升序 / za 名称降序 / lohi 价格升序 / hilo 价格降序"""
        self.wait_loaded()
        first_before = self.driver.find_element(*self.ITEM_NAME).text
        self.select_by_value(self.SORT_SELECT, value)
        # 等列表重排完成：第一个商品名变了，说明 DOM 已经重新渲染
        self.wait_until(lambda d: d.find_element(*self.ITEM_NAME).text != first_before)

    def get_prices(self):
        """返回所有商品价格（float，已去掉 $ 符号）"""
        self.wait_loaded()
        return [float(el.text.replace("$", "")) for el in self.driver.find_elements(*self.ITEM_PRICE)]

    def add_item_by_index(self, index):
        """加购列表中第 index 个商品（从 0 开始）"""
        self.wait_loaded()
        buttons = self.driver.find_elements(*self.ADD_BTNS)
        self.logger.info("加购第 %s 个商品，共 %s 个", index, len(buttons))
        buttons[index].click()