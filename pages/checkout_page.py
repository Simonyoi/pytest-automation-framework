"""结算流程页面对象（覆盖 step-one / step-two / complete 三个页面）"""
from selenium.webdriver.common.by import By

from common.base_page import BasePage


class CheckoutPage(BasePage):
    # —— 第一步：填写收货信息 ——
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BTN = (By.ID, "continue")
    ERROR_MSG = (By.CSS_SELECTOR, "h3[data-test='error']")

    # —— 第二步：确认订单 ——
    FINISH_BTN = (By.ID, "finish")
    TOTAL_LABEL = (By.CLASS_NAME, "summary_total_label")

    # —— 完成页 ——
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")

    def wait_step_one(self):
        """等进入第一步（网址变化 + 姓名输入框可见）"""
        self.wait_url_contains("/checkout-step-one.html")
        return self.wait_visible(self.FIRST_NAME)

    def fill_info(self, first_name, last_name, postal_code):
        """填写收货信息三件套"""
        self.wait_step_one()
        self.input(self.FIRST_NAME, first_name)
        self.input(self.LAST_NAME, last_name)
        self.input(self.POSTAL_CODE, postal_code)

    def continue_to_step_two(self):
        self.click(self.CONTINUE_BTN)

    def wait_step_two(self):
        """等进入第二步（确认订单页）"""
        self.wait_url_contains("/checkout-step-two.html")
        return self.wait_visible(self.FINISH_BTN)

    def get_total(self):
        """订单总价，形如 'Total: $32.39'"""
        return self.get_text(self.TOTAL_LABEL)

    def finish(self):
        self.click(self.FINISH_BTN)

    def wait_complete(self):
        """等进入完成页"""
        self.wait_url_contains("/checkout-complete.html")
        return self.wait_visible(self.COMPLETE_HEADER)

    def get_complete_header(self):
        return self.get_text(self.COMPLETE_HEADER)

    def get_error(self):
        return self.get_text(self.ERROR_MSG)