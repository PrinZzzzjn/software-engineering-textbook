"""统一的接口请求封装。

教学要点（对应第 16、20 章）：
1. 所有页面共用同一个请求入口，避免每个页面各写一套 requests 代码；
2. 自动带上 Authorization: Bearer <token>，token 从 st.session_state 读取；
3. 统一把后端的错误响应转换成 ApiError，页面只需要 try/except 一次；
4. 遇到 401 时清除登录态，提示重新登录。

接口事实以项目参考 duty-simplified 为准：
- 业务接口不设版本前缀，集合路径直接挂在根下且无尾斜杠，例如 /departments；
- 列表只返回 {"items": [...], "total": n}，排序参数由后端固定，前端不传 sort_by；
- 登录是 POST /users/login；健康检查 GET /health 是独立的服务级路由。
"""

from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from config import API_BASE_URL, API_PREFIX, REQUEST_TIMEOUT


class ApiError(Exception):
    """接口调用失败的统一异常。"""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _url(path: str) -> str:
    """拼接完整接口地址，path 以 / 开头。"""
    return f"{API_BASE_URL}{API_PREFIX}{path}"


def _headers() -> dict[str, str]:
    """从 session_state 取令牌，自动加到请求头。"""
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _request(method: str, path: str, **kwargs: Any) -> Any:
    """所有请求的唯一入口：发请求、统一处理错误。"""
    try:
        response = requests.request(
            method,
            _url(path),
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise ApiError(0, f"无法连接后端服务：{exc}") from exc

    # 401：令牌失效，清空登录态，页面会引导用户重新登录
    if response.status_code == 401:
        st.session_state.pop("access_token", None)
        st.session_state.pop("current_user", None)
        raise ApiError(401, "登录已过期，请重新登录")

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        # FastAPI 的参数校验错误是一个列表，这里压平成一句话
        if isinstance(detail, list):
            detail = "；".join(str(item.get("msg", item)) for item in detail)
        raise ApiError(response.status_code, str(detail))

    if not response.content:
        return None
    return response.json()


def get(path: str, params: dict | None = None) -> Any:
    return _request("GET", path, params=params)


def post(path: str, json: dict | None = None) -> Any:
    return _request("POST", path, json=json)


def put(path: str, json: dict | None = None) -> Any:
    return _request("PUT", path, json=json)


def delete(path: str) -> Any:
    return _request("DELETE", path)


def health() -> dict:
    """后端健康检查：/health 是独立的服务级路由，单独处理。"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise ApiError(0, f"后端服务不可用：{exc}") from exc


def login(username: str, password: str) -> dict:
    """登录，并把令牌与用户信息保存到 session_state。"""
    data = _request(
        "POST",
        "/users/login",
        json={"username": username, "password": password},
    )
    st.session_state["access_token"] = data["access_token"]
    st.session_state["current_user"] = data.get("user", {})
    return data
