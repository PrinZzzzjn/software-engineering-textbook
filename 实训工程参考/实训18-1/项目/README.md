# 执勤电子年鉴前端 · 实训 18-1 完成态

在 17-1 多页前端上补齐写操作：单位页增加编辑与删除，并新增人员、哨位、执勤记录三个业务页。所有写操作按「校验—提交—刷新」三步，危险操作二次确认，成功反馈用 flash 跨重跑保留，页码与筛选放进 `session_state`。

## 目录

```text
app.py                  入口：首页 + 登录门禁
auth.py                 登录、登出、require_login
api_client.py           基地址、超时、令牌、错误四统一
config.py               基地址、超时、默认分页
components/table.py     render_table / pagination_bar
components/feedback.py  set_flash / show_flash
pages/1_单位管理.py     列表、搜索、分页、新增、编辑、删除
pages/2_数据统计.py     人员/年份、指标、两张表（沿用 17-1）
pages/3_人员管理.py     筛选、分页、新增、编辑、删除
pages/4_哨位管理.py     筛选、分页、新增、编辑、删除
pages/5_执勤记录.py     筛选、分页、新增、删除
verify_app.py           结构与 AppTest 自测（97 项）
```

## 运行

后端（13-1 项目）：

```powershell
cd ..\..\实训13-1\项目
python -m uvicorn main:app --port 8000
```

前端（本目录）：

```powershell
python -m pip install -r requirements.txt
python verify_app.py
python -m streamlit run app.py
```

`verify_app.py` 末尾应为 `97/97 passed`。账号 `admin / admin123`。

## 写操作约定

| 操作 | 校验 | 提交 | 成功后 |
| --- | --- | --- | --- |
| 新增 | 前端必填/长度 | POST | 回第 1 页 + flash + `st.rerun()` |
| 编辑 | 必填 | PUT（主键禁用） | 保留当前页 + flash + `st.rerun()` |
| 删除 | 勾选二次确认 | DELETE | flash + `st.rerun()`；页空回退一页 |

执勤记录没有 PUT，页面只做新增与删除。删除单位不会级联删除人员与哨位，页面已提示先清理关联数据。
