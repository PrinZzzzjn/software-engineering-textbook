"""实训 16-1 联调自测：真后端 + Streamlit AppTest，不需要打开浏览器。

前置：
1. 后端运行在 http://127.0.0.1:8000（实训 13-1 项目），admin/admin123 可登录；
2. 本目录已安装 streamlit、pandas、requests。

运行：
    python verify_app.py

注意：脚本只新增/删除测试单位 D900、D902，不改动 D001、D002 两条种子数据。
"""

from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest

import api_client

BASE_URL = "http://127.0.0.1:8000"
APP = str(Path(__file__).with_name("app.py"))
TEST_CODE = "D900"
checks = []


def check(name, condition, detail=""):
    checks.append((name, bool(condition), detail))


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def login() -> str:
    resp = requests.post(
        f"{BASE_URL}/users/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def delete_dep(code: str, token: str) -> None:
    requests.delete(f"{BASE_URL}/departments/{code}", headers=headers(token), timeout=10)


def create_dep(code: str, name: str, address: str, token: str) -> None:
    requests.post(
        f"{BASE_URL}/departments",
        json={"dept_code": code, "full_name": name, "address": address},
        headers=headers(token),
        timeout=10,
    )


def cleanup_tests(token: str) -> None:
    """删除自测可能留下的测试单位。"""
    for code in [TEST_CODE, "D902"]:
        delete_dep(code, token)


def ensure_departments(token: str) -> None:
    """确保两条种子单位存在；不存在才补建，不删除已有数据。"""
    for code, name, address in [
        ("D001", "一中队", "一号营区"),
        ("D002", "二中队", "二号营区"),
    ]:
        resp = requests.get(f"{BASE_URL}/departments/{code}", timeout=10)
        if resp.status_code == 404:
            create_dep(code, name, address, token)


def run_app(app: AppTest) -> AppTest:
    app.run()
    if app.exception:
        raise AssertionError(f"页面运行异常：{app.exception}")
    return app


# ----------------------------- 0. 后端预检 ---------------------------------
health = requests.get(f"{BASE_URL}/health", timeout=10)
check("后端 /health 返回 200", health.status_code == 200, health.status_code)
check("health 正文为 healthy", health.json() == {"status": "healthy"}, health.text)

token = login()
cleanup_tests(token)
ensure_departments(token)

# ----------------------------- 1. 未登录 -----------------------------------
app = AppTest.from_file(APP, default_timeout=60)
run_app(app)
check("未登录显示登录页", app.title and app.title[0].value == "🗂️ 执勤电子年鉴", app.title)
check("登录表单有用户名与密码", len(app.text_input) == 2, len(app.text_input))
check("未登录不渲染表格", len(app.dataframe) == 0, len(app.dataframe))

# ----------------------------- 2. 错误密码 ---------------------------------
app.text_input(key="login_username").set_value("admin")
app.text_input(key="login_password").set_value("wrong-password")
app.button(key="login_submit").click()
run_app(app)
check(
    "错误密码给出提示",
    any("用户名或密码错误" in item.value for item in app.error),
    [item.value for item in app.error],
)

# ----------------------------- 3. 正确登录 ---------------------------------
app.text_input(key="login_username").set_value("admin")
app.text_input(key="login_password").set_value("admin123")
app.button(key="login_submit").click()
run_app(app)
check("登录后进入单位页", app.title and app.title[0].value == "🏢 单位管理", app.title)
check("令牌已写入会话", bool(app.session_state.get("access_token")), "access_token")
check("单位总数指标为 2", app.metric[0].value == "2", app.metric[0].value)
check("种子单位 2 行", len(app.dataframe[0].value) == 2, len(app.dataframe[0].value))
codes = list(app.dataframe[0].value["dept_code"])
check("表格字段为契约字段", codes == ["D001", "D002"], codes)

# ----------------------------- 4. 空态 -------------------------------------
app.text_input(key="keyword").set_value("不存在的单位").run()
check(
    "空数据显示提示",
    any("没有符合条件" in item.value for item in app.info),
    [item.value for item in app.info],
)
check("空数据不渲染空表", len(app.dataframe) == 0, len(app.dataframe))

app.text_input(key="keyword").set_value("").run()
check("清空搜索后回到 2 行", len(app.dataframe[0].value) == 2, len(app.dataframe[0].value))

# ----------------------------- 5. 新增成功 ---------------------------------
app.text_input(key="new_dept_code").set_value(TEST_CODE)
app.text_input(key="new_full_name").set_value("联调测试分队")
app.text_input(key="new_address").set_value("训练场")
app.button(key="submit_dept").click()
run_app(app)
check("新增成功提示", any("已新增" in item.value for item in app.success), [s.value for s in app.success])
check("新增后 3 行", len(app.dataframe[0].value) == 3, len(app.dataframe[0].value))
check(
    "新增行可在表中看到",
    TEST_CODE in list(app.dataframe[0].value["dept_code"]),
    list(app.dataframe[0].value["dept_code"]),
)

# ----------------------------- 6. 重复编码 400 -----------------------------
app.text_input(key="new_dept_code").set_value("D001")
app.text_input(key="new_full_name").set_value("重复单位")
app.button(key="submit_dept").click()
run_app(app)
check("重复编码提示已存在", any("已存在" in item.value for item in app.error), [e.value for e in app.error])
check("拒绝后仍为 3 行", len(app.dataframe[0].value) == 3, len(app.dataframe[0].value))

# ----------------------------- 7. 字段校验 422 -----------------------------
app.text_input(key="new_dept_code").set_value("D901")
app.text_input(key="new_full_name").set_value("超" * 101)
app.button(key="submit_dept").click()
run_app(app)
error_texts = [item.value for item in app.error]
check("422 提示为可读字符串", any("100" in text for text in error_texts), error_texts)
check("422 已压平不是字典列表", all(not text.startswith("[") for text in error_texts), error_texts)

# ----------------------------- 8. 路径错误 404 -----------------------------
api_client.API_PREFIX = "/api/v1"
run_app(app)
check("错误前缀触发 404", any("Not Found" in item.value for item in app.error), [e.value for e in app.error])
api_client.API_PREFIX = ""
run_app(app)
check("恢复前缀后列表可用", len(app.dataframe[0].value) == 3, len(app.dataframe[0].value))

# ----------------------------- 9. 令牌失效 401 -----------------------------
# GET /departments 是公开接口，无效令牌仍能读；写接口要求管理员，才会返回 401
app.session_state["access_token"] = "invalid-token"
app.text_input(key="new_dept_code").set_value("D902")
app.text_input(key="new_full_name").set_value("过期令牌测试")
app.button(key="submit_dept").click()
run_app(app)
check(
    "401 后给出重新登录提示",
    any("登录已过期" in item.value for item in app.warning),
    [item.value for item in app.warning],
)
check("401 后回到登录页", app.title and app.title[0].value == "🗂️ 执勤电子年鉴", app.title)
check("401 后令牌已清除", "access_token" not in app.session_state, "access_token")

# ----------------------------- 10. 清理 ------------------------------------
cleanup_tests(token)
final = requests.get(
    f"{BASE_URL}/departments", params={"page": 1, "page_size": 100}, timeout=10
).json()
final_codes = [item["dept_code"] for item in final["items"]]
check(
    "清理后种子仍在且无测试单位",
    "D001" in final_codes
    and "D002" in final_codes
    and TEST_CODE not in final_codes
    and "D902" not in final_codes,
    final_codes,
)

# ----------------------------- 输出 ----------------------------------------
passed = sum(1 for _, ok, _ in checks if ok)
for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")
print(f"\n{passed}/{len(checks)} passed")
if passed != len(checks):
    raise SystemExit(1)
