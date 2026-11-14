"""Web UI 页面基类：封装 Selenium 常用操作 + 显式等待。

所有页面对象类继承它，实现具体页面元素和操作。
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from common.logger import get_logger


class BasePage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.logger = get_logger("web")

    def find(self, locator):
        """locator 形如 (By.ID, "user-name")"""
        return self.driver.find_element(*locator)

    def wait_visible(self, locator, timeout=None):
        """显式等待元素可见，替代 time.sleep"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_present(self, locator, timeout=None):
        """显式等待元素出现在 DOM 中（不一定可见），用于页面就绪判定"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_url_contains(self, fragment, timeout=None):
        """显式等待 URL 包含指定片段，用于页面跳转断言"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            EC.url_contains(fragment)
        )

    def count(self, locator):
        """返回当前匹配元素个数（依赖调用方已确认页面就绪）"""
        return len(self.driver.find_elements(*locator))

    def wait_count(self, locator, expected,timeout=None):
        """显式等待元素个数达到预期"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            lambda d: len(d.find_elements(*locator)) == expected
        )

    def click(self, locator):
        self.logger.info("点击元素 %s", locator)
        self.wait_visible(locator).click()

    def input(self, locator, text):
        self.logger.info("输入 %s -> %s", locator, text)
        el = self.wait_visible(locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, locator):
        return self.wait_visible(locator).text

    def is_displayed(self, locator):
        try:
            return self.find(locator).is_displayed()
        except Exception:
            return False

    def wait_until(self, condition, timeout=None):
        """通用显式等待：condition(driver) 返回真值即结束"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(condition)

    def wait_text(self, locator, expected, timeout=None):
        """显式等待元素的文本等于 expected"""
        return WebDriverWait(self.driver, timeout or self.timeout).until(
            lambda d: d.find_element(*locator).text == expected
        )

    def select_by_value(self, locator, value):
        """原生 <select> 下拉框，按 value 属性选择选项"""
        Select(self.wait_visible(locator)).select_by_value(value)