# 执勤电子年鉴前端 · 实训 20-1 完成态

在 19-1 仪表盘的基础上做前端综合实践：按用户真实路径联调，把「状态码 → 用户提示」收拢到统一错误组件，并用十步清单与交付材料证明这套页面能一起交付。业务读写、主题、图表与状态规则保持不变。

## 目录

```text
.streamlit/config.toml 主题：浅色底、青绿主色、深色正文
app.py                  入口：首页 + 登录门禁
auth.py                 登录、登出、require_login
api_client.py           基地址、超时、令牌、错误四统一
config.py               基地址、超时、默认分页
components/table.py     render_table / pagination_bar
components/feedback.py  set_flash / show_flash
components/errors.py    show_api_error：状态码到可读提示的统一映射
pages/1_单位管理.py     列表、搜索、分页、新增、编辑、删除
pages/2_数据统计.py     侧边栏筛选、四个指标卡、折线图、柱状图、明细
pages/3_人员管理.py     筛选、分页、新增、编辑、删除
pages/4_哨位管理.py     筛选、分页、新增、编辑、删除
pages/5_执勤记录.py     筛选、分页、新增、删除
verify_app.py           统一错误、十步联调与 18-1/19-1 回归自测
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

## 统一错误处理

所有接口异常都来自 `api_client.ApiError`，页面只调用一个函数：

```python
try:
    data = api.get("/departments", params=params)
except api.ApiError as exc:
    show_api_error(exc)
    st.stop()
```

| 状态码 | 含义 | 页面表现 |
| --- | --- | --- |
| 401 | 没登录 / 令牌过期 | 清空会话、回登录页并提示「登录已过期」 |
| 403 | 登录了但没权限 | 「当前账号没有权限执行该操作」 |
| 404 | 资源不存在 | 「数据不存在，可能已被删除」 |
| 422 | 参数校验失败 | 「提交内容有误：<具体字段原因>」 |
| 500 | 后端异常 | 「服务器开小差了，请稍后重试或联系管理员」 |
| 0 | 连不上后端 | 「无法连接后端服务：<原因>」 |

登录页的 401 是账号密码错误，仍由 `auth.render_login()` 单独提示，不进入统一映射。

## 十步用户路径联调

`verify_app.py` 的「3.5」节按教材 20.2 的清单逐步断言：未登录被拦 → 登录 → 列表 → 搜索 → 新增 → 编辑 → 删除 → 统计 → 切换条件 → 退出。运行结束会额外打印这十步的通过情况。

## 写操作约定（沿用 18-1）

| 操作 | 校验 | 提交 | 成功后 |
| --- | --- | --- | --- |
| 新增 | 前端必填/长度 | POST | 回第 1 页 + flash + `st.rerun()` |
| 编辑 | 必填 | PUT（主键禁用） | 保留当前页 + flash + `st.rerun()` |
| 删除 | 勾选二次确认 | DELETE | flash + `st.rerun()`；页空回退一页 |

执勤记录没有 PUT，页面只做新增与删除。空数据不是错误，用 `st.info` 提示。
