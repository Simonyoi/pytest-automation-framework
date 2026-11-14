"""用户增删改查接口服务层"""
from common.base_api import BaseApi


class UserApi(BaseApi):
    def list_users(self, page=1):
        return self.get("/users", params={"page": page})

    def get_user(self, user_id):
        return self.get(f"/users/{user_id}")

    def create_user(self, name, job):
        return self.post("/users", json={"name": name, "job": job})

    def update_user(self, user_id, name, job):
        return self.put(f"/users/{user_id}", json={"name": name, "job": job})

    def delete_user(self, user_id):
        return self.delete(f"/users/{user_id}")
