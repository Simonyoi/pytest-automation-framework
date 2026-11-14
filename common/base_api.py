"""接口请求基类：封装 requests，统一日志、超时、重试与鉴权。

各接口服务类继承它，实现具体业务接口。
"""
import time

import requests

from common.logger import get_logger

# 仅服务端瞬时异常重试；429 是配额信号（如 reqres 匿名 demo 40 次/天），重试无意义
RETRY_STATUS_CODES = (500, 502, 503, 504)


class BaseApi:
    def __init__(self, base_url, timeout=10, retries=0, backoff=1, api_key=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = max(0, retries)
        self.backoff = max(0, backoff)
        self.session = requests.Session()
        if api_key:
            # 配置了 key 就走独立配额，规避公共 demo 的限流
            self.session.headers.update({"x-api-key": api_key})
        self.logger = get_logger("api")

    def request(self, method, path, **kwargs):
        url = self.base_url + path
        kwargs.setdefault("timeout", self.timeout)
        for attempt in range(self.retries + 1):
            try:
                self.logger.info(
                    "请求 %s %s | params=%s | data=%s | json=%s",
                    method.upper(), url,
                    kwargs.get("params"), kwargs.get("data"), kwargs.get("json"),
                )
                resp = self.session.request(method, url, **kwargs)
            except requests.exceptions.RequestException as e:
                # 覆盖超时、连接失败、分块传输中断等全部 requests 异常
                if attempt >= self.retries:
                    self.logger.error("请求最终失败 %s %s | %s: %s", method.upper(), url,
                                      e.__class__.__name__, e)
                    raise
                self.logger.warning("请求异常(%s)，第 %s 次重试", e.__class__.__name__, attempt + 1)
                self._sleep(attempt)
                continue

            self.logger.info("响应 [%s] %s", resp.status_code, resp.text[:500])
            if resp.status_code == 429:
                self.logger.error(
                    "接口限流：anonymous demo 有每日请求上限，请在 config/config.yaml 的 api.api_key 填入免费 key"
                )
            if resp.status_code in RETRY_STATUS_CODES and attempt < self.retries:
                self.logger.warning("响应状态 %s 触发重试，第 %s 次", resp.status_code, attempt + 1)
                self._sleep(attempt)
                continue
            return resp

        raise RuntimeError(f"请求未返回响应: {method.upper()} {url}")  # pragma: no cover

    def _sleep(self, attempt):
        """退避等待：第 n 次重试等待 backoff * n 秒，避免连续冲击服务端"""
        if self.backoff:
            time.sleep(self.backoff * (attempt + 1))

    def close(self):
        """释放连接池（fixture 中显式调用）"""
        self.session.close()

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request("PUT", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
