"""登录/注册接口服务层"""
from common.base_api import BaseApi


class LoginApi(BaseApi):
    def login(self, email, password):
        return self.post("/login", json={"email": email, "password": password})

    def register(self, email, password):
        return self.post("/register", json={"email": email, "password": password})
