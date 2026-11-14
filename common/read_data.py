"""读取 data/ 目录下的 yaml 测试数据（数据驱动用）"""
import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_test_data(rel_path):
    """读取 data/ 目录下的 yaml 文件，如 get_test_data("api/login_data.yaml")"""
    full_path = os.path.join(BASE_DIR, "data", rel_path)
    return read_yaml(full_path)
