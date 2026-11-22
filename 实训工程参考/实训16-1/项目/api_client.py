"""统一的接口请求封装（教材 16.3 的最小版）。

四个统一：
1. 地址统一：BASE_URL 与路径前缀都在 config.py；
2. 请求头统一：_headers 自动注入 Authorization: Bearer <token>；
3. 超时统一：REQUEST_TIMEOUT；
4. 错误统一：所有失败都转成 ApiError，页面只捕获这一种异常。

两条易错结论：
- 401 要清除登录态，避免拿着过期令牌反复请求；
- FastAPI 的 422 detail 是一个列表，显示前要压平成一句话。
"""

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


def _headers() -> dict:
    """从 session_state 取令牌，自动加到请求头。"""
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _request(method: str, path: str, **kwargs):
    """所有请求的唯一入口：发请求、统一处理错误。"""
    try:
        resp = requests.request(
            method,
            _url(path),
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise ApiError(0, f"无法连接后端服务：{exc}") from exc

    # 401：令牌失效，清空登录态，页面会引导用户重新登录
    if resp.status_code == 401:
        st.session_state.pop("access_token", None)
        raise ApiError(401, "登录已过期，请重新登录")

    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        # FastAPI 的参数校验错误是一个列表，这里压平成一句话
        if isinstance(detail, list):
            detail = "；".join(str(item.get("msg", item)) for item in detail)
        raise ApiError(resp.status_code, str(detail))

    return resp.json() if resp.content else None


def get(path: str, params: dict | None = None):
    return _request("GET", path, params=params)


def post(path: str, json: dict | None = None):
    return _request("POST", path, json=json)


def put(path: str, json: dict | None = None):
    return _request("PUT", path, json=json)


def delete(path: str):
    return _request("DELETE", path)
