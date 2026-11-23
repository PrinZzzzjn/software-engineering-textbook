# 内网 `/docs` 本地化（教师用）

## 一、问题

FastAPI 默认的 `/docs` 页面会从公网 CDN 加载 Swagger UI 的 JS/CSS。授课机完全内网时，页面会空白；`/openapi.json` 不受影响。

## 二、不采用 `fastapi-offline` 的原因

`fastapi-offline` 能用，但它是额外的第三方依赖，当前离线清单没有锁定，版本和行为不如 `swagger-ui-bundle` 可控；它还要求把 `FastAPI` 改成 `FastAPIOffline`，会改动学员代码。仓库的离线清单已经包含 `swagger-ui-bundle`，直接用它。

## 三、方案：授课机 venv 预置

1. 在授课机虚拟环境安装 `swagger-ui-bundle`（离线 wheelhouse 已包含）。
2. 把本目录的 `sitecustomize.py` 复制到该 venv 的 `site-packages/` 目录。
   - Python 启动时会自动导入 `sitecustomize`。
   - 若环境已有 `sitecustomize.py`，不要覆盖；改用 `.pth` 方式：
     把本文件改名为 `sitecustomize_offline_docs.py`，放在 `site-packages/`，
     再新建 `offline_docs.pth`，内容一行：`import sitecustomize_offline_docs`。
3. 学员仍用 `app = FastAPI()` 与 `uvicorn main:app --reload --port 8000`，代码不变。

## 四、验证

2026-11-23 在开发机做了两步核对：

1. `python -m py_compile sitecustomize.py` 通过；
2. 用一个假的 `swagger_ui_bundle` 包加载补丁，`FastAPI()` 后路由包含 `/docs` 与 `/static/swagger`，说明 monkeypatch 逻辑生效。

真实 `swagger_ui_bundle` 当前未装在开发机，页面渲染待授课机安装后复验：

启动任意 FastAPI 应用后：

```bash
curl -s http://127.0.0.1:8000/docs | grep -o "/static/swagger/[^\"']*" | head
```

预期看到 `swagger-ui-bundle.js` 与 `swagger-ui.css` 的本地路径，而不是 `cdn.jsdelivr.net`。

再在浏览器打开 `/docs`：

- 页面能渲染，Swagger UI 正常显示端点；
- 浏览器开发者工具的 Network 里没有公网请求；
- 断网后刷新仍然可用。

## 五、失效时的备用通道

若 `sitecustomize` 未生效或 `swagger-ui-bundle` 未安装：

1. 用 `http://127.0.0.1:8000/openapi.json` 查看接口清单；
2. 用 `curl` 或 `/docs` 之外的请求脚本完成验收；
3. 教师把现象记录在授课机环境说明中，不把空白页当作学员代码错误。

## 六、边界

- 只处理默认 `/docs`；应用显式 `docs_url=None` 时不处理。
- 不修改学员 `main.py`，不新增学员依赖。
- 不把静态资源副本提交进仓库；资源来自 `swagger-ui-bundle` 包。
