"""读取 config.yaml 配置，提供全局单例 config 对象。

用法：
    from config.read_config import config
    config.get("web", "base_url")
    config.get("api", "base_url", default="xxx")
"""
import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def get(self, *keys, default=None):
        """按层级取配置，如 get("web", "account", "username")"""
        node = self._data
        for key in keys:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return default
        return node


config = Config()
