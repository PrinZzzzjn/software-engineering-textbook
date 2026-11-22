# 执勤电子年鉴前端 · 实训 19-1 完成态

在 18-1 写操作页面的基础上做界面优化与数据可视化：用 `.streamlit/config.toml` 统一主题，把数据统计页改成「指标卡 + 两张图 + 明细」的仪表盘；其余四页的业务逻辑、写操作与状态规则保持不变。

## 目录

```text
.streamlit/config.toml 主题：浅色底、青绿主色、深色正文
app.py                  入口：首页 + 登录门禁
auth.py                 登录、登出、require_login
api_client.py           基地址、超时、令牌、错误四统一
config.py               基地址、超时、默认分页
components/table.py     render_table / pagination_bar
components/feedback.py  set_flash / show_flash
pages/1_单位管理.py     列表、搜索、分页、新增、编辑、删除
pages/2_数据统计.py     侧边栏筛选、四个指标卡、折线图、柱状图、明细
pages/3_人员管理.py     筛选、分页、新增、编辑、删除
pages/4_哨位管理.py     筛选、分页、新增、编辑、删除
pages/5_执勤记录.py     筛选、分页、新增、删除
verify_app.py           结构、主题、仪表盘与写操作回归自测
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

账号 `admin / admin123`。改完 `.streamlit/config.toml` 必须重启 Streamlit，主题才生效。

## 统计页结构

| 层级 | 内容 | 用到的接口 |
| --- | --- | --- |
| 筛选 | 侧边栏选人员与年份 | `GET /personnel` |
| 总览 | 四个 `st.metric`：天数、时长、记录数、高峰时段数 | `/analytics/*` |
| 趋势 | `st.line_chart` 画 24 小时分布 | `/analytics/duty-time-distribution` |
| 对比 | `st.bar_chart` 画月度天数 | `/analytics/staff-duty-yearly` |
| 明细 | `st.dataframe` 列出当年执勤记录 | `GET /duty-records` |

指标数字全部取自接口，不在前端手填；没有记录的年份给出提示，不画空图。

## 写操作约定（沿用 18-1）

| 操作 | 校验 | 提交 | 成功后 |
| --- | --- | --- | --- |
| 新增 | 前端必填/长度 | POST | 回第 1 页 + flash + `st.rerun()` |
| 编辑 | 必填 | PUT（主键禁用） | 保留当前页 + flash + `st.rerun()` |
| 删除 | 勾选二次确认 | DELETE | flash + `st.rerun()`；页空回退一页 |

执勤记录没有 PUT，页面只做新增与删除。
