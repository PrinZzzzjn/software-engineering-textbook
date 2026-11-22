"""实训 17-1 自测：目录结构 + 页面发现 + 登录守卫 + 两页可用性。

前置：
1. 后端运行在 http://127.0.0.1:8000（实训 13-1 项目），admin/admin123 可登录；
2. 本目录已安装 streamlit、pandas、requests。

运行：
    python verify_app.py

注意：脚本只新增/删除测试单位 D910–D916，不改动 D001、D002 两条种子数据。
D910–D915 由脚本直接建，用于凑出两页；D916 由页面「新增单位」表单创建。
"""

import sys
from pathlib import Path

import requests
from streamlit.source_util import page_icon_and_name, page_sort_key
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

BASE_URL = "http://127.0.0.1:8000"
APP = str(ROOT / "app.py")
PAGE_DEPT = str(ROOT / "pages" / "1_单位管理.py")
PAGE_STATS = str(ROOT / "pages" / "2_数据统计.py")
TEST_CODES = [f"D91{i}" for i in range(7)]  # D910–D916
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


def cleanup_tests(token: str) -> None:
    for code in TEST_CODES:
        requests.delete(
            f"{BASE_URL}/departments/{code}", headers=headers(token), timeout=10
        )


def create_dep(code: str, name: str, token: str) -> None:
    requests.post(
        f"{BASE_URL}/departments",
        json={"dept_code": code, "full_name": name, "address": "测试营区"},
        headers=headers(token),
        timeout=10,
    )


def ensure_departments(token: str) -> None:
    for code, name, address in [
        ("D001", "一中队", "一号营区"),
        ("D002", "二中队", "二号营区"),
    ]:
        resp = requests.get(f"{BASE_URL}/departments/{code}", timeout=10)
        if resp.status_code == 404:
            requests.post(
                f"{BASE_URL}/departments",
                json={"dept_code": code, "full_name": name, "address": address},
                headers=headers(token),
                timeout=10,
            )


def run_app(app: AppTest) -> AppTest:
    app.run()
    if app.exception:
        raise AssertionError(f"页面运行异常：{app.exception}")
    return app


def has_text(items, needle: str) -> bool:
    return any(needle in str(item.value) for item in items)


# ----------------------------- 0. 结构与页面发现 ---------------------------
required = [
    ROOT / "app.py",
    ROOT / "auth.py",
    ROOT / "api_client.py",
    ROOT / "config.py",
    ROOT / "pages" / "1_单位管理.py",
    ROOT / "pages" / "2_数据统计.py",
    ROOT / "components" / "table.py",
]
missing = [p.name for p in required if not p.exists()]
check("七类文件各就各位", not missing, missing)

page_files = sorted((ROOT / "pages").glob("*.py"), key=page_sort_key)
nav_names = [page_icon_and_name(path)[1] for path in page_files]
check("pages 下恰有两个页面", len(page_files) == 2, [p.name for p in page_files])
check(
    "数字前缀决定顺序、去掉前缀成为导航名",
    nav_names == ["单位管理", "数据统计"],
    nav_names,
)

dept_source = (ROOT / "pages" / "1_单位管理.py").read_text(encoding="utf-8")
stats_source = (ROOT / "pages" / "2_数据统计.py").read_text(encoding="utf-8")
check(
    "单位页在第一次请求之前调用守卫",
    0 <= dept_source.find("auth.require_login()") < dept_source.find("api.get"),
    "require_login 位置",
)
check(
    "统计页在第一次请求之前调用守卫",
    0 <= stats_source.find("auth.require_login()") < stats_source.find("api.get"),
    "require_login 位置",
)

# ----------------------------- 1. 后端与数据准备 ---------------------------
health = requests.get(f"{BASE_URL}/health", timeout=10)
check("后端 /health 返回 200", health.status_code == 200, health.status_code)

token = login()
cleanup_tests(token)
ensure_departments(token)
# 只建 6 条：加两条种子共 8 条，每页 5 条时正好两页（5 + 3）
for index, code in enumerate(TEST_CODES[:6], start=1):
    create_dep(code, f"分页测试分队{index}", token)

# ----------------------------- 2. 入口：未登录 -----------------------------
app = AppTest.from_file(APP, default_timeout=60)
run_app(app)
check("未登录显示登录页", app.title and app.title[0].value == "🗂️ 执勤电子年鉴", app.title)
check("未登录不渲染功能导航", not has_text(app.subheader, "功能导航"), "subheader")

# ----------------------------- 3. 入口：登录闭环 ---------------------------
app.text_input(key="login_username").set_value("admin")
app.text_input(key="login_password").set_value("wrong-password")
app.button(key="login_submit").click()
run_app(app)
check("错误密码给出提示", has_text(app.error, "用户名或密码错误"), [e.value for e in app.error])

app.text_input(key="login_username").set_value("admin")
app.text_input(key="login_password").set_value("admin123")
app.button(key="login_submit").click()
run_app(app)
check("登录后进入首页", has_text(app.subheader, "功能导航"), [s.value for s in app.subheader])
check("首页列出两个页面", has_text(app.markdown, "单位管理") and has_text(app.markdown, "数据统计"), "导航说明")
check("令牌已写入会话", bool(app.session_state.get("access_token")), "access_token")

# ----------------------------- 3.1 页面切换 ---------------------------------
app.switch_page("pages/1_单位管理.py")
run_app(app)
check("从首页切到单位页", app.title and app.title[0].value == "🏢 单位管理", app.title)
check("切换后列表可用", len(app.dataframe[0].value) == 8, len(app.dataframe[0].value))
check("切换后仍保持登录", bool(app.session_state.get("access_token")), "access_token")

app.switch_page("pages/2_数据统计.py")
run_app(app)
check("从单位页切到统计页", app.title and app.title[0].value == "📊 数据统计", app.title)
check("统计页指标已渲染", len(app.metric) == 3, len(app.metric))

# ----------------------------- 4. 子页面守卫 ------------------------------
guard_app = AppTest.from_file(PAGE_DEPT, default_timeout=60)
run_app(guard_app)
check("未登录访问单位页被拦截", has_text(guard_app.warning, "请先登录"), [w.value for w in guard_app.warning])
check("被拦截时不渲染单位标题", not has_text(guard_app.title, "单位管理"), guard_app.title)
check("被拦截时不发列表请求", len(guard_app.dataframe) == 0, len(guard_app.dataframe))

stats_guard = AppTest.from_file(PAGE_STATS, default_timeout=60)
run_app(stats_guard)
check("未登录访问统计页被拦截", has_text(stats_guard.warning, "请先登录"), [w.value for w in stats_guard.warning])
check("被拦截时不渲染统计标题", not has_text(stats_guard.title, "数据统计"), stats_guard.title)

# ----------------------------- 5. 单位页：四区与列表 -----------------------
dept_app = AppTest.from_file(PAGE_DEPT, default_timeout=60)
run_app(dept_app)
dept_app.session_state["access_token"] = token
dept_app.session_state["current_user"] = {"username": "admin", "role": "admin"}
run_app(dept_app)

check("单位页标题区", dept_app.title and dept_app.title[0].value == "🏢 单位管理", dept_app.title)
check(
    "区域顺序为筛选→内容→操作",
    [s.value for s in dept_app.subheader] == ["单位列表", "新增单位"],
    [s.value for s in dept_app.subheader],
)
check("单位总数指标为 8", dept_app.metric[0].value == "8", dept_app.metric[0].value)
check("默认页显示 8 行", len(dept_app.dataframe[0].value) == 8, len(dept_app.dataframe[0].value))
check("分页条显示第 1 / 1 页", has_text(dept_app.markdown, "第 1 / 1 页，共 8 条"), "分页文本")

# ----------------------------- 6. 分页 -------------------------------------
dept_app.selectbox(key="dept_page_size").select(5)
run_app(dept_app)
check("每页 5 条时显示 5 行", len(dept_app.dataframe[0].value) == 5, len(dept_app.dataframe[0].value))
check("分页条显示第 1 / 2 页", has_text(dept_app.markdown, "第 1 / 2 页，共 8 条"), "分页文本")

dept_app.button(key="dept_next").click()
run_app(dept_app)
check("翻到第 2 页显示 3 行", len(dept_app.dataframe[0].value) == 3, len(dept_app.dataframe[0].value))
check("分页条显示第 2 / 2 页", has_text(dept_app.markdown, "第 2 / 2 页，共 8 条"), "分页文本")

# ----------------------------- 7. 搜索与空态 -------------------------------
dept_app.text_input(key="dept_keyword").set_value("一中队")
run_app(dept_app)
check("搜索命中 1 行", len(dept_app.dataframe[0].value) == 1, len(dept_app.dataframe[0].value))
check("搜索后回到第 1 页", has_text(dept_app.markdown, "第 1 / 1 页，共 1 条"), "分页文本")

dept_app.text_input(key="dept_keyword").set_value("不存在的单位")
run_app(dept_app)
check("空结果显示提示", has_text(dept_app.info, "没有符合条件"), [i.value for i in dept_app.info])
check("空结果不渲染表格", len(dept_app.dataframe) == 0, len(dept_app.dataframe))

dept_app.text_input(key="dept_keyword").set_value("")
dept_app.selectbox(key="dept_page_size").select(10)
run_app(dept_app)
check("清空搜索后回到 8 行", len(dept_app.dataframe[0].value) == 8, len(dept_app.dataframe[0].value))

# ----------------------------- 8. 新增与错误 -------------------------------
dept_app.text_input(key="new_dept_code").set_value("D916")
dept_app.text_input(key="new_full_name").set_value("页面新增分队")
dept_app.text_input(key="new_address").set_value("训练场")
dept_app.button(key="submit_dept").click()
run_app(dept_app)
check("新增成功提示", has_text(dept_app.success, "已新增"), [s.value for s in dept_app.success])
check("新增后 9 行", len(dept_app.dataframe[0].value) == 9, len(dept_app.dataframe[0].value))
check(
    "新增行可在表中看到",
    "D916" in list(dept_app.dataframe[0].value["dept_code"]),
    list(dept_app.dataframe[0].value["dept_code"]),
)

dept_app.text_input(key="new_dept_code").set_value("D001")
dept_app.text_input(key="new_full_name").set_value("重复单位")
dept_app.button(key="submit_dept").click()
run_app(dept_app)
check("重复编码提示已存在", has_text(dept_app.error, "已存在"), [e.value for e in dept_app.error])
check("拒绝后仍为 9 行", len(dept_app.dataframe[0].value) == 9, len(dept_app.dataframe[0].value))

dept_app.text_input(key="new_dept_code").set_value("D918")
dept_app.text_input(key="new_full_name").set_value("超" * 101)
dept_app.button(key="submit_dept").click()
run_app(dept_app)
check("422 提示为可读字符串", has_text(dept_app.error, "100"), [e.value for e in dept_app.error])
check(
    "422 已压平不是字典列表",
    all(not str(e.value).startswith("[") for e in dept_app.error),
    [e.value for e in dept_app.error],
)

# ----------------------------- 9. 令牌失效回登录 ---------------------------
dept_app.session_state["access_token"] = "invalid-token"
dept_app.text_input(key="new_dept_code").set_value("D919")
dept_app.text_input(key="new_full_name").set_value("过期令牌测试")
dept_app.button(key="submit_dept").click()
run_app(dept_app)
check("401 后提示重新登录", has_text(dept_app.warning, "登录已过期"), [w.value for w in dept_app.warning])
check("401 后回到登录页", dept_app.title and dept_app.title[0].value == "🗂️ 执勤电子年鉴", dept_app.title)
check("401 后令牌已清除", "access_token" not in dept_app.session_state, "access_token")

# ----------------------------- 10. 统计页 --------------------------------
stats_app = AppTest.from_file(PAGE_STATS, default_timeout=60)
run_app(stats_app)
stats_app.session_state["access_token"] = token
stats_app.session_state["current_user"] = {"username": "admin", "role": "admin"}
run_app(stats_app)

check("统计页标题区", stats_app.title and stats_app.title[0].value == "📊 数据统计", stats_app.title)
check("人员下拉默认 P001", "P001" in stats_app.selectbox(key="stats_person").value, stats_app.selectbox(key="stats_person").value)
check("执勤天数为 2", stats_app.metric[0].value == "2", stats_app.metric[0].value)
check("执勤时长为 16", float(stats_app.metric[1].value) == 16.0, stats_app.metric[1].value)
check("记录条数为 3", stats_app.metric[2].value == "3", stats_app.metric[2].value)
check("月度分布有 3、4 月两行", len(stats_app.dataframe[0].value) == 2, stats_app.dataframe[0].value)
check(
    "月度行与口径一致",
    list(stats_app.dataframe[0].value["month"]) == [3, 4],
    list(stats_app.dataframe[0].value["month"]),
)
check("高峰时段为 8 时", has_text(stats_app.caption, "8 时"), [c.value for c in stats_app.caption])
check("24 小时分布为 8 时与 13 时两行", len(stats_app.dataframe[1].value) == 2, stats_app.dataframe[1].value)
check(
    "8 时记录 2 条、13 时记录 1 条",
    list(stats_app.dataframe[1].value["count"]) == [2, 1],
    list(stats_app.dataframe[1].value["count"]),
)

stats_app.selectbox(key="stats_year").select("2025")
run_app(stats_app)
check("无记录年份显示空态", has_text(stats_app.info, "没有执勤记录"), [i.value for i in stats_app.info])
check("无记录年份天数为 0", stats_app.metric[0].value == "0", stats_app.metric[0].value)

# ----------------------------- 11. 清理 -----------------------------------
cleanup_tests(token)
final = requests.get(
    f"{BASE_URL}/departments", params={"page": 1, "page_size": 100}, timeout=10
).json()
final_codes = [item["dept_code"] for item in final["items"]]
check(
    "清理后种子仍在且无测试单位",
    "D001" in final_codes
    and "D002" in final_codes
    and not any(code.startswith("D91") for code in final_codes),
    final_codes,
)

# ----------------------------- 输出 ---------------------------------------
passed = sum(1 for _, ok, _ in checks if ok)
for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")
print(f"\n{passed}/{len(checks)} passed")
if passed != len(checks):
    raise SystemExit(1)
