"""用户增删改查接口测试用例"""
import allure
import pytest


@allure.feature("接口-用户CRUD")
class TestUserCrud:

    @allure.story("用户列表分页")
    @pytest.mark.smoke
    @pytest.mark.parametrize("page", [1, 2])
    def test_list_users(self, user_api, page):
        resp = user_api.list_users(page)
        assert resp.status_code == 200, f"列表接口异常: {resp.status_code} {resp.text[:200]}"
        data = resp.json()
        assert "data" in data
        assert len(data["data"]) > 0
        # 分页元信息自洽：当前页号、总页数、每页条数要能互相验证
        assert data["page"] == page, f"返回页号不符: {data['page']} != {page}"
        assert 1 <= page <= data["total_pages"], f"页号超出总页数: {page}/{data['total_pages']}"
        assert len(data["data"]) <= data["per_page"]

    @allure.story("查询单个用户")
    def test_get_user(self, user_api, user_dataset):
        user_id = user_dataset["data"][0]["id"]
        resp = user_api.get_user(user_id)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == user_id

    @allure.story("查询不存在的用户")
    def test_get_user_not_found(self, user_api, user_dataset):
        # 以数据集总数为基准推导不存在的 id，数据规模变化时用例依然成立
        missing_id = user_dataset["total"] + 1000
        resp = user_api.get_user(missing_id)
        assert resp.status_code == 404, f"期望 404，实际 {resp.status_code}"

    @allure.story("创建用户")
    @pytest.mark.smoke
    def test_create_user(self, user_api):
        resp = user_api.create_user("morpheus", "leader")
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "morpheus"
        assert body["job"] == "leader"
        assert body["id"], "创建用户未返回 id"

    @allure.story("更新用户")
    def test_update_user(self, user_api, user_dataset):
        user_id = user_dataset["data"][0]["id"]
        resp = user_api.update_user(user_id, "morpheus", "zion resident")
        assert resp.status_code == 200
        body = resp.json()
        assert body["job"] == "zion resident"
        assert "updatedAt" in body, "更新用户未返回 updatedAt"

    @allure.story("删除用户")
    def test_delete_user(self, user_api, user_dataset):
        user_id = user_dataset["data"][-1]["id"]
        resp = user_api.delete_user(user_id)
        assert resp.status_code == 204
        assert resp.text == "", "204 响应体应为空"

    @allure.story("分页元信息自洽")
    def test_pagination_meta(self, user_api):
        body = user_api.list_users(1).json()
        total = body["total"]
        per_page = body["per_page"]
        total_pages = body["total_pages"]

        # 向上取整的整数写法：ceil(total / per_page) == (total + per_page - 1) // per_page
        expected = (total + per_page - 1) // per_page
        assert total_pages == expected, (
            f"总页数不符: {total_pages} != ceil({total}/{per_page})={expected}"
        )

    @allure.story("分页数据不重叠")
    def test_pages_not_overlap(self, user_api):
        page1 = user_api.list_users(1).json()["data"]
        page2 = user_api.list_users(2).json()["data"]

        ids1 = {u["id"] for u in page1}      # 集合推导式
        ids2 = {u["id"] for u in page2}

        duplicated = ids1 & ids2             # & 是集合交集
        assert duplicated == set(), f"两页出现重复用户: {sorted(duplicated)}"

    @allure.story("用户字段完整性")
    def test_user_fields(self, user_api):
        users = user_api.list_users(1).json()["data"]
        required = {"id", "email", "first_name", "last_name", "avatar"}

        for user in users:
            missing = required - user.keys()          # 差集：要的 - 有的 = 缺的
            assert not missing, f"用户 {user.get('id')} 缺少字段: {missing}"
            assert "@" in user["email"], f"邮箱格式异常: {user['email']}"

    @allure.story("响应头 Content-Type")
    def test_response_content_type(self, user_api):
        resp = user_api.list_users(1)
        content_type = resp.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Content-Type 异常: {content_type}"