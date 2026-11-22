"""实训 19-1 自测：主题、仪表盘、指标卡与图表，以及 18-1 写操作回归。

前置：
1. 后端运行在 http://127.0.0.1:8000（实训 13-1 项目），admin/admin123 可登录；
2. 本目录已安装 streamlit、pandas、requests。

运行：
    python verify_app.py

测试数据只用 D901–D905、P901–P905、W901–W905，以及脚本新建后删除的执勤记录；
不改动 D001/D002、P001/P002、W001/W002 与四条种子执勤记录。
"""

import json
import sys
import tomllib
from datetime import date, time
from pathlib import Path

import requests
from streamlit.source_util import page_icon_and_name, page_sort_key
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

BASE = "http://127.0.0.1:8000"
APP = str(ROOT / "app.py")
PAGE_DEPT = str(ROOT / "pages" / "1_单位管理.py")
PAGE_STATS = str(ROOT / "pages" / "2_数据统计.py")
PAGE_PERSON = str(ROOT / "pages" / "3_人员管理.py")
PAGE_STATION = str(ROOT / "pages" / "4_哨位管理.py")
PAGE_DUTY = str(ROOT / "pages" / "5_执勤记录.py")
THEME_CONFIG = ROOT / ".streamlit" / "config.toml"

TEST_DEPTS = [f"D90{i}" for i in range(1, 6)]  # D901–D905
TEST_PERS = [f"P90{i}" for i in range(1, 6)]  # P901–P905
TEST_STATIONS = [f"W90{i}" for i in range(1, 6)]  # W901–W905
checks = []


def check(name, condition, detail=""):
    checks.append((name, bool(condition), detail))


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def api_get(path: str, params: dict | None = None):
    return requests.get(f"{BASE}{path}", params=params, timeout=10)


def api_post(path: str, payload: dict, token: str):
    return requests.post(f"{BASE}{path}", json=payload, headers=headers(token), timeout=10)


def api_put(path: str, payload: dict, token: str):
    return requests.put(f"{BASE}{path}", json=payload, headers=headers(token), timeout=10)


def api_delete(path: str, token: str):
    return requests.delete(f"{BASE}{path}", headers=headers(token), timeout=10)


def login() -> str:
    resp = requests.post(
        f"{BASE}/users/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def cleanup(token: str) -> None:
    """先删测试执勤记录，再删测试人员/哨位，最后删测试单位（无级联删除）。"""
    data = api_get("/duty-records", {"page": 1, "page_size": 100}).json()
    for record in data.get("items", []):
        if (
            record["personnel_certificate_number"] in TEST_PERS
            or record["workstation_id"] in TEST_STATIONS
        ):
            api_delete(f"/duty-records/{record['id']}", token)
    for cert in TEST_PERS:
        api_delete(f"/personnel/{cert}", token)
    for station in TEST_STATIONS:
        api_delete(f"/workstations/{station}", token)
    for code in TEST_DEPTS:
        api_delete(f"/departments/{code}", token)


def ensure_seed_data(token: str) -> None:
    for code, name, address in [
        ("D001", "一中队", "一号营区"),
        ("D002", "二中队", "二号营区"),
    ]:
        if api_get(f"/departments/{code}").status_code == 404:
            api_post(
                "/departments",
                {"dept_code": code, "full_name": name, "address": address},
                token,
            )
    for cert, name, dept, rank in [
        ("P001", "张伟", "D001", "一级值班员"),
        ("P002", "李娜", "D002", "二级值班员"),
    ]:
        if api_get(f"/personnel/{cert}").status_code == 404:
            api_post(
                "/personnel",
                {
                    "certificate_number": cert,
                    "name": name,
                    "dept_code": dept,
                    "rank": rank,
                },
                token,
            )
    for station, name, dept in [
        ("W001", "一号哨位", "D001"),
        ("W002", "二号哨位", "D002"),
    ]:
        if api_get(f"/workstations/{station}").status_code == 404:
            api_post(
                "/workstations",
                {"workstation_id": station, "name": name, "dept_code": dept},
                token,
            )


def build_fixtures(token: str) -> None:
    for index, code in enumerate(["D901", "D902", "D903", "D904"], start=1):
        api_post(
            "/departments",
            {"dept_code": code, "full_name": f"测试{index}队", "address": "测试营区"},
            token,
        )
    for cert, name, dept, rank in [
        ("P901", "测试员甲", "D901", "一级值班员"),
        ("P902", "测试员乙", "D902", "二级值班员"),
    ]:
        api_post(
            "/personnel",
            {
                "certificate_number": cert,
                "name": name,
                "dept_code": dept,
                "rank": rank,
            },
            token,
        )
    for station, name, dept in [
        ("W901", "测试哨位一", "D901"),
        ("W902", "测试哨位二", "D902"),
    ]:
        api_post(
            "/workstations",
            {"workstation_id": station, "name": name, "dept_code": dept},
            token,
        )


def run_app(app: AppTest) -> AppTest:
    app.run()
    if app.exception:
        raise AssertionError(f"页面运行异常：{app.exception}")
    return app


def has_text(items, needle: str) -> bool:
    return any(needle in str(item.value) for item in items)


def disabled(element) -> bool:
    return bool(getattr(element.proto, "disabled", False))


def authed(page_path: str, token: str) -> AppTest:
    app = AppTest.from_file(page_path, default_timeout=60)
    app.session_state["access_token"] = token
    app.session_state["current_user"] = {"username": "admin", "role": "admin"}
    return run_app(app)


# ----------------------------- 0. 结构与页面发现 ---------------------------
required = [
    ROOT / "app.py",
    ROOT / "auth.py",
    ROOT / "api_client.py",
    ROOT / "config.py",
    ROOT / "components" / "table.py",
    ROOT / "components" / "feedback.py",
    THEME_CONFIG,
    ROOT / "pages" / "1_单位管理.py",
    ROOT / "pages" / "2_数据统计.py",
    ROOT / "pages" / "3_人员管理.py",
    ROOT / "pages" / "4_哨位管理.py",
    ROOT / "pages" / "5_执勤记录.py",
]
missing = [path.name for path in required if not path.exists()]
check("结构与组件各就各位", not missing, missing)

page_files = sorted((ROOT / "pages").glob("*.py"), key=page_sort_key)
nav_names = [page_icon_and_name(path)[1] for path in page_files]
check("pages 下恰有五个页面", len(page_files) == 5, [p.name for p in page_files])
check(
    "数字前缀决定顺序、去掉前缀成为导航名",
    nav_names == ["单位管理", "数据统计", "人员管理", "哨位管理", "执勤记录"],
    nav_names,
)

for label, path in [
    ("单位页", PAGE_DEPT),
    ("统计页", PAGE_STATS),
    ("人员页", PAGE_PERSON),
    ("哨位页", PAGE_STATION),
    ("记录页", PAGE_DUTY),
]:
    source = Path(path).read_text(encoding="utf-8")
    check(
        f"{label}在第一次请求之前调用守卫",
        0 <= source.find("auth.require_login()") < source.find("api.get"),
        "require_login 位置",
    )

feedback_source = (ROOT / "components" / "feedback.py").read_text(encoding="utf-8")
check(
    "反馈组件提供 set_flash 与 show_flash",
    "def set_flash" in feedback_source and "def show_flash" in feedback_source,
    "feedback.py",
)
check(
    "show_flash 取出后清除，避免重复提示",
    'pop("_flash"' in feedback_source,
    "feedback.py",
)
client_source = (ROOT / "api_client.py").read_text(encoding="utf-8")
check(
    "api_client 提供 put 与 delete",
    "def put" in client_source and "def delete" in client_source,
    "api_client.py",
)

# ----------------------------- 0.1 主题配置 ---------------------------------
theme = tomllib.loads(THEME_CONFIG.read_text(encoding="utf-8"))
theme_values = theme.get("theme", {})
theme_keys = [
    "base",
    "primaryColor",
    "backgroundColor",
    "secondaryBackgroundColor",
    "textColor",
    "font",
]
check("config.toml 有 [theme] 节", "theme" in theme, list(theme))
check("主题常用键齐全", all(key in theme_values for key in theme_keys), theme_values)
check(
    "浅色底 + 青绿主色 + 深色正文",
    theme_values.get("base") == "light"
    and theme_values.get("primaryColor") == "#0F766E"
    and theme_values.get("backgroundColor") == "#F8FAFC"
    and theme_values.get("textColor") == "#0F172A",
    theme_values,
)
check(
    "关闭 Streamlit 使用统计",
    theme.get("browser", {}).get("gatherUsageStats") is False,
    theme.get("browser"),
)

stats_source = Path(PAGE_STATS).read_text(encoding="utf-8")
check("统计页用侧边栏放筛选", "with st.sidebar" in stats_source, "pages/2_数据统计.py")
check(
    "统计页使用 line_chart 与 bar_chart",
    "st.line_chart" in stats_source and "st.bar_chart" in stats_source,
    "pages/2_数据统计.py",
)
check(
    "指标字段来自统计接口",
    all(
        field in stats_source
        for field in ["total_duty_days", "total_duty_hours", "total_records"]
    ),
    "pages/2_数据统计.py",
)
check(
    "空数据先提示再画图",
    "暂不绘制" in stats_source and "st.info" in stats_source,
    "pages/2_数据统计.py",
)

# ----------------------------- 1. 后端与数据准备 ---------------------------
health = requests.get(f"{BASE}/health", timeout=10)
check("后端 /health 返回 200", health.status_code == 200, health.status_code)

token = login()
cleanup(token)
ensure_seed_data(token)
build_fixtures(token)

# ----------------------------- 2. 入口与登录 -------------------------------
app = AppTest.from_file(APP, default_timeout=60)
run_app(app)
check("未登录显示登录页", app.title and app.title[0].value == "🗂️ 执勤电子年鉴", app.title)
check("未登录不渲染功能导航", not has_text(app.subheader, "功能导航"), "subheader")

app.text_input(key="login_username").set_value("admin")
app.text_input(key="login_password").set_value("wrong-password")
app.button(key="login_submit").click()
run_app(app)
check("错误密码给出提示", has_text(app.error, "用户名或密码错误"), [e.value for e in app.error])

app.text_input(key="login_password").set_value("admin123")
app.button(key="login_submit").click()
run_app(app)
check("登录后进入首页", has_text(app.subheader, "功能导航"), [s.value for s in app.subheader])
check(
    "首页列出五个页面",
    all(
        has_text(app.markdown, name)
        for name in ["单位管理", "数据统计", "人员管理", "哨位管理", "执勤记录"]
    ),
    "导航说明",
)
check("令牌已写入会话", bool(app.session_state.get("access_token")), "access_token")

# ----------------------------- 3. 五页守卫 --------------------------------
for label, path, title in [
    ("单位页", PAGE_DEPT, "单位管理"),
    ("统计页", PAGE_STATS, "数据统计"),
    ("人员页", PAGE_PERSON, "人员管理"),
    ("哨位页", PAGE_STATION, "哨位管理"),
    ("记录页", PAGE_DUTY, "执勤记录"),
]:
    guard = AppTest.from_file(path, default_timeout=60)
    run_app(guard)
    check(
        f"未登录访问{label}被拦截",
        has_text(guard.warning, "请先登录"),
        [w.value for w in guard.warning],
    )
    check(
        f"被拦截时不渲染{label}标题",
        not has_text(guard.title, title),
        guard.title,
    )
    check(f"被拦截时{label}不发列表请求", len(guard.dataframe) == 0, len(guard.dataframe))

# ----------------------------- 4. 统计仪表盘 ------------------------------
stats = authed(PAGE_STATS, token)
check("统计页标题区", stats.title and stats.title[0].value == "📊 数据统计", stats.title)
check(
    "侧边栏有两个筛选",
    [box.key for box in stats.sidebar.selectbox] == ["stats_person", "stats_year"],
    [box.key for box in stats.sidebar.selectbox],
)
check("指标卡共 4 个", len(stats.metric) == 4, [m.label for m in stats.metric])
check("指标：执勤天数 2", stats.metric[0].value == "2", stats.metric[0].value)
check("指标：时长 16.0", float(stats.metric[1].value) == 16.0, stats.metric[1].value)
check("指标：记录 3", stats.metric[2].value == "3", stats.metric[2].value)
check("指标：高峰时段数 1", stats.metric[3].value == "1", stats.metric[3].value)

charts = stats.get("vega_lite_chart")
specs = [json.loads(element.proto.spec) for element in charts]
check("仪表盘有 2 张图", len(specs) == 2, len(specs))


def chart_mark(spec: dict) -> str | None:
    layer = spec.get("layer") or [spec]
    return (layer[0].get("mark") or {}).get("type")


marks = [chart_mark(spec) for spec in specs]
check("图表类型为折线与柱状", sorted(marks) == ["bar", "line"], marks)
check("两张图高度均为 260", all(spec.get("height") == 260 for spec in specs), [
    spec.get("height") for spec in specs
])
spec_text = json.dumps(specs, ensure_ascii=False)
check("图表使用统一色 #0D9488", spec_text.count("#0D9488") >= 2, spec_text.count("#0D9488"))
check(
    "折线画 count、柱状画 days",
    '"field": "count"' in spec_text and '"field": "days"' in spec_text,
    "y 字段",
)
check("横轴为小时与月份", "小时" in spec_text and "月份" in spec_text, "索引名")
check("高峰时段写在图下", has_text(stats.caption, "高峰时段：8 时"), [c.value for c in stats.caption])

detail_tables = [
    element.value
    for element in stats.dataframe
    if "workstation_id" in getattr(element.value, "columns", [])
]
check("明细表显示 3 行", bool(detail_tables) and len(detail_tables[0]) == 3,
      [len(t) for t in detail_tables])

stats.selectbox(key="stats_year").select("2025")
run_app(stats)
check(
    "无记录年份指标归零",
    [m.value for m in stats.metric] == ["0", "0.0", "0", "0"],
    [m.value for m in stats.metric],
)
check("无记录年份不画空图", len(stats.get("vega_lite_chart")) == 0, "vega_lite_chart")
check(
    "无记录年份给出提示",
    has_text(stats.info, "没有执勤记录") and has_text(stats.info, "没有执勤明细"),
    [i.value for i in stats.info],
)

# ----------------------------- 5. 单位页：编辑、删除、状态 ------------------
dept = authed(PAGE_DEPT, token)
check("单位页标题区", dept.title and dept.title[0].value == "🏢 单位管理", dept.title)
check(
    "单位页区域顺序为列表→新增→编辑→删除",
    [s.value for s in dept.subheader]
    == ["单位列表", "新增单位", "编辑单位", "删除单位"],
    [s.value for s in dept.subheader],
)
check("单位总数为 6", dept.metric[0].value == "6", dept.metric[0].value)
check("默认页显示 6 行", len(dept.dataframe[0].value) == 6, len(dept.dataframe[0].value))

dept.selectbox(key="dept_page_size").select(5)
run_app(dept)
check("每页 5 条时显示 5 行", len(dept.dataframe[0].value) == 5, len(dept.dataframe[0].value))
check("分页条第 1 / 2 页", has_text(dept.markdown, "第 1 / 2 页，共 6 条"), "分页文本")

dept.button(key="dept_next").click()
run_app(dept)
check("翻到第 2 页显示 1 行", len(dept.dataframe[0].value) == 1, len(dept.dataframe[0].value))
check("分页条第 2 / 2 页", has_text(dept.markdown, "第 2 / 2 页，共 6 条"), "分页文本")

# 4.1 编辑：回填 → 保存 → 保留第 2 页
dept.selectbox(key="dept_edit_select").select("D904 - 测试4队")
run_app(dept)
dept.text_input(key="edit_dept_name_D904").set_value("测试4队（改）")
dept.text_input(key="edit_dept_address_D904").set_value("新营区")
dept.button(key="dept_save").click()
run_app(dept)
check(
    "编辑后仍在第 2 页",
    has_text(dept.markdown, "第 2 / 2 页，共 6 条"),
    [m.value for m in dept.markdown],
)
check("编辑后反馈已消费", "_flash" not in dept.session_state, "_flash")
saved = api_get("/departments/D904").json()
check("编辑已写入后端", saved.get("full_name") == "测试4队（改）", saved)
check(
    "编辑结果在表格中可见",
    "测试4队（改）" in list(dept.dataframe[0].value["full_name"]),
    list(dept.dataframe[0].value["full_name"]),
)

# 4.2 切换搜索条件时页码重置为 1
dept.text_input(key="dept_keyword").set_value("测试")
run_app(dept)
check("搜索变化后回到第 1 页", has_text(dept.markdown, "第 1 / 1 页，共 4 条"), "分页文本")
check("搜索命中 4 行", len(dept.dataframe[0].value) == 4, len(dept.dataframe[0].value))

dept.text_input(key="dept_keyword").set_value("")
run_app(dept)
dept.button(key="dept_next").click()
run_app(dept)
check("清空搜索后可再次翻到第 2 页", has_text(dept.markdown, "第 2 / 2 页，共 6 条"), "分页文本")

# 4.3 删除：未勾选时按钮禁用；确认后删除；当前页空了页码回退
dept.selectbox(key="dept_delete_select").select("D904 - 测试4队（改）")
run_app(dept)
check("未勾选确认时删除按钮禁用", disabled(dept.button(key="dept_delete")), "dept_delete")
dept.checkbox(key="dept_delete_confirm_D904").check()
run_app(dept)
check("勾选确认后删除按钮可用", not disabled(dept.button(key="dept_delete")), "dept_delete")
dept.button(key="dept_delete").click()
run_app(dept)
check(
    "删除最后一条后页码回退到第 1 页",
    has_text(dept.markdown, "第 1 / 1 页，共 5 条"),
    [m.value for m in dept.markdown],
)
check("删除后接口返回 404", api_get("/departments/D904").status_code == 404, "D904")

# 4.4 新增、重复与 422
dept.selectbox(key="dept_page_size").select(20)
run_app(dept)
dept.text_input(key="new_dept_code").set_value("D905")
dept.text_input(key="new_full_name").set_value("测试5队")
dept.text_input(key="new_address").set_value("训练场")
dept.button(key="submit_dept").click()
run_app(dept)
check("新增后总数为 6", dept.metric[0].value == "6", dept.metric[0].value)
check("新增行在表格中可见", "D905" in list(dept.dataframe[0].value["dept_code"]), "D905")
check("新增反馈已消费", "_flash" not in dept.session_state, "_flash")

dept.text_input(key="new_dept_code").set_value("D901")
dept.text_input(key="new_full_name").set_value("重复单位")
dept.button(key="submit_dept").click()
run_app(dept)
check("重复编码提示已存在", has_text(dept.error, "已存在"), [e.value for e in dept.error])

dept.text_input(key="new_dept_code").set_value("D906")
dept.text_input(key="new_full_name").set_value("超" * 101)
dept.button(key="submit_dept").click()
run_app(dept)
check("422 提示为可读字符串", has_text(dept.error, "100"), [e.value for e in dept.error])
check(
    "422 已压平不是字典列表",
    all(not str(e.value).startswith("[") for e in dept.error),
    [e.value for e in dept.error],
)

# ----------------------------- 6. 人员页 -----------------------------------
person = authed(PAGE_PERSON, token)
check("人员页标题区", person.title and person.title[0].value == "👤 人员管理", person.title)
check("人员总数为 4", person.metric[0].value == "4", person.metric[0].value)

person.text_input(key="person_name").set_value("测试员甲")
run_app(person)
check("按姓名筛选命中 1 行", len(person.dataframe[0].value) == 1, len(person.dataframe[0].value))
person.text_input(key="person_name").set_value("")
run_app(person)

person.selectbox(key="person_dept").select("D901 - 测试1队")
run_app(person)
check("按单位筛选命中 1 行", len(person.dataframe[0].value) == 1, len(person.dataframe[0].value))
check(
    "筛选结果为单位 D901",
    list(person.dataframe[0].value["dept_code"]) == ["D901"],
    list(person.dataframe[0].value["dept_code"]),
)
person.selectbox(key="person_dept").select("全部")
run_app(person)

person.text_input(key="new_person_cert").set_value("P903")
person.text_input(key="new_person_name").set_value("测试员丙")
person.selectbox(key="new_person_dept").select("D903 - 测试3队")
person.text_input(key="new_person_rank").set_value("三级值班员")
person.button(key="create_person_submit").click()
run_app(person)
check("人员新增后总数为 5", person.metric[0].value == "5", person.metric[0].value)
created_person = api_get("/personnel/P903")
check("人员新增已写入后端", created_person.status_code == 200, created_person.status_code)

person.selectbox(key="person_edit_select").select("P903 - 测试员丙")
run_app(person)
person.text_input(key="edit_person_rank_P903").set_value("四级值班员")
person.button(key="person_save").click()
run_app(person)
check(
    "人员编辑已写入后端",
    api_get("/personnel/P903").json().get("rank") == "四级值班员",
    api_get("/personnel/P903").json(),
)

person.selectbox(key="person_delete_select").select("P903 - 测试员丙")
run_app(person)
check("人员删除未确认时禁用", disabled(person.button(key="person_delete")), "person_delete")
person.checkbox(key="person_delete_confirm_P903").check()
run_app(person)
person.button(key="person_delete").click()
run_app(person)
check("人员删除后接口返回 404", api_get("/personnel/P903").status_code == 404, "P903")
check("人员删除后总数为 4", person.metric[0].value == "4", person.metric[0].value)

# ----------------------------- 7. 哨位页 -----------------------------------
station = authed(PAGE_STATION, token)
check("哨位页标题区", station.title and station.title[0].value == "🛡️ 哨位管理", station.title)
check("哨位总数为 4", station.metric[0].value == "4", station.metric[0].value)

station.selectbox(key="station_dept").select("D901 - 测试1队")
run_app(station)
check("哨位按单位筛选命中 1 行", len(station.dataframe[0].value) == 1, len(station.dataframe[0].value))
station.selectbox(key="station_dept").select("全部")
run_app(station)

station.text_input(key="new_station_id").set_value("W903")
station.text_input(key="new_station_name").set_value("测试哨位三")
station.selectbox(key="new_station_dept").select("D903 - 测试3队")
station.button(key="create_station_submit").click()
run_app(station)
check("哨位新增后总数为 5", station.metric[0].value == "5", station.metric[0].value)
check("哨位新增已写入后端", api_get("/workstations/W903").status_code == 200, "W903")

station.selectbox(key="station_edit_select").select("W903 - 测试哨位三")
run_app(station)
station.text_input(key="edit_station_name_W903").set_value("测试哨位三（改）")
station.checkbox(key="edit_station_active_W903").uncheck()
station.button(key="station_save").click()
run_app(station)
edited_station = api_get("/workstations/W903").json()
check(
    "哨位编辑已写入后端",
    edited_station.get("name") == "测试哨位三（改）" and edited_station.get("is_active") == 0,
    edited_station,
)

station.selectbox(key="station_delete_select").select("W903 - 测试哨位三（改）")
run_app(station)
check("哨位删除未确认时禁用", disabled(station.button(key="station_delete")), "station_delete")
station.checkbox(key="station_delete_confirm_W903").check()
run_app(station)
station.button(key="station_delete").click()
run_app(station)
check("哨位删除后接口返回 404", api_get("/workstations/W903").status_code == 404, "W903")

# ----------------------------- 8. 执勤记录页 --------------------------------
duty = authed(PAGE_DUTY, token)
check("执勤记录页标题区", duty.title and duty.title[0].value == "📋 执勤记录", duty.title)
check("执勤记录总数为 4", duty.metric[0].value == "4", duty.metric[0].value)

duty.selectbox(key="duty_person").select("P001 - 张伟")
run_app(duty)
check("按人员筛选命中 3 行", len(duty.dataframe[0].value) == 3, len(duty.dataframe[0].value))
duty.selectbox(key="duty_person").select("全部")
run_app(duty)

duty.selectbox(key="new_duty_person").select("P901 - 测试员甲")
duty.selectbox(key="new_duty_station").select("W901 - 测试哨位一")
duty.date_input(key="new_duty_start_date").set_value(date(2026, 5, 1))
duty.time_input(key="new_duty_start_time").set_value(time(8, 0))
duty.date_input(key="new_duty_end_date").set_value(date(2026, 5, 1))
duty.time_input(key="new_duty_end_time").set_value(time(12, 0))
duty.button(key="create_duty_submit").click()
run_app(duty)
check("执勤记录新增后总数为 5", duty.metric[0].value == "5", duty.metric[0].value)
created_records = api_get(
    "/duty-records",
    {"personnel_certificate_number": "P901", "page": 1, "page_size": 100},
).json()
check("执勤记录新增已写入后端", created_records.get("total") == 1, created_records)
created = created_records["items"][0]
created_id = created["id"]

# 7.1 同一哨位时段重叠 → 后端 400
duty.selectbox(key="new_duty_person").select("P901 - 测试员甲")
duty.selectbox(key="new_duty_station").select("W901 - 测试哨位一")
duty.date_input(key="new_duty_start_date").set_value(date(2026, 5, 1))
duty.time_input(key="new_duty_start_time").set_value(time(10, 0))
duty.date_input(key="new_duty_end_date").set_value(date(2026, 5, 1))
duty.time_input(key="new_duty_end_time").set_value(time(14, 0))
duty.button(key="create_duty_submit").click()
run_app(duty)
check(
    "时段重叠时显示后端 detail",
    has_text(duty.error, "已有执勤安排"),
    [e.value for e in duty.error],
)
check("冲突后总数仍为 5", duty.metric[0].value == "5", duty.metric[0].value)

# 7.2 前端校验：开始时间必须早于结束时间
duty.selectbox(key="new_duty_person").select("P901 - 测试员甲")
duty.selectbox(key="new_duty_station").select("W901 - 测试哨位一")
duty.date_input(key="new_duty_start_date").set_value(date(2026, 5, 2))
duty.time_input(key="new_duty_start_time").set_value(time(8, 0))
duty.date_input(key="new_duty_end_date").set_value(date(2026, 5, 1))
duty.time_input(key="new_duty_end_time").set_value(time(12, 0))
duty.button(key="create_duty_submit").click()
run_app(duty)
check(
    "前端拦截开始晚于结束",
    has_text(duty.error, "必须早于"),
    [e.value for e in duty.error],
)

# 7.3 删除记录：未确认禁用 → 确认后删除
record_label = (
    f"#{created['id']} {created['personnel_certificate_number']} "
    f"{created['start_time']} → {created['end_time']}"
)
duty.selectbox(key="duty_delete_select").select(record_label)
run_app(duty)
check("记录删除未确认时禁用", disabled(duty.button(key="duty_delete")), "duty_delete")
duty.checkbox(key=f"duty_delete_confirm_{created_id}").check()
run_app(duty)
duty.button(key="duty_delete").click()
run_app(duty)
check("记录删除后总数回到 4", duty.metric[0].value == "4", duty.metric[0].value)
check(
    "记录删除后接口返回 404",
    api_get(f"/duty-records/{created_id}").status_code == 404,
    created_id,
)

# ----------------------------- 9. 令牌失效回登录 ---------------------------
dept.session_state["access_token"] = "invalid-token"
dept.text_input(key="new_dept_code").set_value("D909")
dept.text_input(key="new_full_name").set_value("过期令牌测试")
dept.button(key="submit_dept").click()
run_app(dept)
check("401 后提示重新登录", has_text(dept.warning, "登录已过期"), [w.value for w in dept.warning])
check("401 后回到登录页", has_text(dept.title, "执勤电子年鉴"), dept.title)
check("401 后令牌已清除", "access_token" not in dept.session_state, "access_token")

# ----------------------------- 10. 清理与结果 -------------------------------
cleanup(token)
remaining = api_get("/departments", {"page": 1, "page_size": 100}).json()
remaining_codes = [item["dept_code"] for item in remaining.get("items", [])]
check("清理后测试单位全部删除", not any(c in remaining_codes for c in TEST_DEPTS), remaining_codes)
check(
    "种子单位仍在",
    "D001" in remaining_codes and "D002" in remaining_codes,
    remaining_codes,
)

passed = sum(1 for _, ok, _ in checks if ok)
for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + ("" if ok else f" -> {detail}"))
print(f"\n{passed}/{len(checks)} passed")
sys.exit(0 if passed == len(checks) else 1)
