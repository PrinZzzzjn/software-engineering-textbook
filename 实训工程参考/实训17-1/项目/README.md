# 实训 17-1 项目：多页面前端（完成态）

配套教材第 17 章与「◆ 实训 17-1」。把 16-1 的单页单位管理拆成多页面应用，并新增数据统计页。

## 运行

后端（实训 13-1，端口 8000）：

```powershell
cd ..\..\实训13-1\项目
python -m uvicorn main:app --port 8000
```

前端（本目录）：

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python verify_app.py
python -m streamlit run app.py
```

浏览器打开 <http://127.0.0.1:8501>，账号 `admin / admin123`。

## 目录

```text
app.py                  # 入口：首页 + 登录门禁
auth.py                 # 登录、登出、require_login
api_client.py           # 请求四统一（与 16-1 一致）
config.py               # 地址、超时、默认分页
components/table.py     # render_table / pagination_bar
pages/1_单位管理.py     # 四区 + 搜索 + 分页 + 新增
pages/2_数据统计.py     # 人员/年份 + 指标 + 月度与时段表
verify_app.py           # 教师自测，59 项
```

## 演示路径

1. 未登录直接访问 `http://127.0.0.1:8501/单位管理`，应被拦截；
2. 登录后首页说明两个页面，左侧边栏自动生成导航；
3. 单位页：每页条数切到 5，翻到第 2 页；搜索「一中队」；新增 D916；
4. 统计页：人员选 P001 - 张伟、年份 2026，查看 2 天 / 16 小时 / 3 条记录；年份切 2025 看空态。

## 自测

`python verify_app.py` 需要后端在 8000 运行，覆盖 59 项，末尾应为 `59/59 passed`。脚本只增删 D910–D916，不动 D001、D002。

## 说明

- 本页不做编辑、删除（18-1），不做图表（19-1）；
- 后端排序固定，前端不传 `sort_by`；
- `pages/` 下的文件名即导航名，新增页面等于新增文件。
