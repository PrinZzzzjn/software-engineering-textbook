"""统一错误提示组件（教材 20.3）。

五个页面各写一套 try/except，提示就会不一致；把「状态码 → 用户可读提示」
收拢到 show_api_error() 一处，页面只保留 `show_api_error(exc)` 与必要的 `st.stop()`。

处理策略：
- 401：清空登录态，回登录页并说明原因；
- 403：登录了但权限不够，不重试；
- 404：数据不存在，可能已被删除，提示后刷新列表；
- 422：显示具体字段问题（api_client 已把列表压平成一句话）；
- 500：后端异常，前端只提示稍后重试，根因看后端日志；
- 0：连不上后端（ApiError(0)），提示检查服务是否启动。

提示里不出现令牌、密码与服务器路径；堆栈只留在后端日志。
"""

import streamlit as st

import api_client as api


def show_api_error(exc: api.ApiError) -> None:
    """把 ApiError 转成一条用户可读的提示。

    401 必须走统一入口：清空会话后重跑，页面守卫会把用户带回登录页。
    """
    status_code = getattr(exc, "status_code", -1)
    detail = getattr(exc, "detail", str(exc))

    if status_code == 401:
        st.session_state.clear()
        st.session_state["login_notice"] = "登录已过期，请重新登录"
        st.rerun()
    elif status_code == 403:
        st.error("当前账号没有权限执行该操作")
    elif status_code == 404:
        st.error("数据不存在，可能已被删除")
    elif status_code == 422:
        st.error(f"提交内容有误：{detail}")
    elif status_code == 500:
        st.error("服务器开小差了，请稍后重试或联系管理员")
    elif status_code == 0:
        st.error(f"无法连接后端服务：{detail}")
    else:
        st.error(detail)
