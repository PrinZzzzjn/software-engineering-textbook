"""实训 15-1 页面自测：用 Streamlit AppTest 驱动组件，不依赖浏览器。

运行（在项目目录下）：
    python verify_app.py

覆盖：初始渲染、指标、搜索、空态、复选框、新增、重复编码、清空搜索。
"""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).with_name("app.py"))
checks = []


def check(name, condition, detail=""):
    checks.append((name, bool(condition), detail))


def run_app():
    app = AppTest.from_file(APP, default_timeout=30).run()
    if app.exception:
        raise AssertionError(f"页面运行异常：{app.exception}")
    return app


# 1. 初始渲染
app = run_app()
check("标题存在", app.title and app.title[0].value == "🏢 单位管理", app.title[0].value)
metric_values = [item.value for item in app.metric]
check("指标三项", len(metric_values) == 3, metric_values)
check("单位总数 12", metric_values[0] == "12", metric_values)
rows = app.dataframe[0].value
check("表格 12 行", len(rows) == 12, len(rows))
check("表格列中文配置生效", "dept_code" in rows.columns, list(rows.columns))

# 2. 搜索
app.text_input(key="keyword").set_value("保障").run()
check("搜索后无异常", not app.exception)
filtered_rows = app.dataframe[0].value
check("搜索“保障”命中 4 条", len(filtered_rows) == 4, len(filtered_rows))
check("筛选指标同步", app.metric[2].value == "4", app.metric[2].value)

# 3. 空态
app.text_input(key="keyword").set_value("不存在").run()
check("空结果有提示", any("没有符合条件" in item.value for item in app.info), app.info)
check("空结果不渲染表格", len(app.dataframe) == 0, len(app.dataframe))

# 4. 复选框
app.text_input(key="keyword").set_value("").run()
app.checkbox(key="only_with_address").set_value(True).run()
check("只看有地址 11 条", len(app.dataframe[0].value) == 11, len(app.dataframe[0].value))

# 5. 新增
app.checkbox(key="only_with_address").set_value(False).run()
app.text_input(key="new_dept_code").set_value("D013")
app.text_input(key="new_full_name").set_value("试点分队")
app.text_input(key="new_address").set_value("试点营区")
app.button(key="submit_dept").click().run()
check("新增后无异常", not app.exception)
check("新增成功提示", any("已新增" in item.value for item in app.success), app.success)
check("新增后 13 行", len(app.dataframe[0].value) == 13, len(app.dataframe[0].value))
check(
    "新增行内容正确",
    any(item["dept_code"] == "D013" for item in app.dataframe[0].value.to_dict("records")),
    "D013",
)

# 6. 重复编码
app.text_input(key="new_dept_code").set_value("D001")
app.text_input(key="new_full_name").set_value("重复单位")
app.button(key="submit_dept").click().run()
check("重复编码被拒绝", any("已存在" in item.value for item in app.error), app.error)
check("拒绝后仍为 13 行", len(app.dataframe[0].value) == 13, len(app.dataframe[0].value))

# 7. 清空搜索按钮
app.text_input(key="keyword").set_value("一中队").run()
before_clear = len(app.dataframe[0].value)
app.button(key="clear_keyword").click().run()
check(
    "清空搜索恢复全部",
    before_clear < 13 and len(app.dataframe[0].value) == 13,
    len(app.dataframe[0].value),
)

# 输出结果
passed = sum(1 for _, ok, _ in checks if ok)
for name, ok, detail in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")
print(f"\n{passed}/{len(checks)} passed")
if passed != len(checks):
    raise SystemExit(1)
