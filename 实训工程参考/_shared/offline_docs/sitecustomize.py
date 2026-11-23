"""授课机 venv 启动钩子：让 FastAPI 的 /docs 使用本地 Swagger UI。

为什么需要：
FastAPI 默认的 /docs 从公网 CDN 加载 Swagger UI 的 JS/CSS；完全内网时页面空白。
本文件在 Python 启动时把 FastAPI 的默认文档路由改成加载本地 swagger_ui_bundle 资源，
学员的 main.py 不需要改，仍是 `app = FastAPI()` 与 `uvicorn main:app`。

安装（授课机，仓库外）：
1. 在授课机 venv 安装 swagger-ui-bundle（离线 wheelhouse 已包含）。
2. 把本文件复制到该 venv 的 site-packages/ 目录；Python 启动时会自动导入 sitecustomize。
   或者新建一个 .pth 文件，内容为 `import sitecustomize_offline_docs`，
   并把本文件改名为 sitecustomize_offline_docs.py 放在同一目录。

注意：
- 只处理默认文档路由；应用显式传 docs_url=None 时不处理。
- 如果 swagger_ui_bundle 未安装，静默跳过，不影响应用启动。
- 不要把本文件的内容抄进学员 main.py；它是环境基础设施，不是业务代码。
"""

from __future__ import annotations

try:
    from swagger_ui_bundle import swagger_ui_path
except Exception:  # 未安装时不影响任何应用
    swagger_ui_path = None


if swagger_ui_path:
    try:
        from fastapi import FastAPI
        from fastapi.openapi.docs import get_swagger_ui_html
        from fastapi.staticfiles import StaticFiles

        _original_init = FastAPI.__init__

        if not getattr(FastAPI, "_offline_docs_patched", False):

            def _init_with_local_docs(self, *args, **kwargs):
                docs_path = kwargs.get("docs_url", "/docs")
                if docs_path is None:
                    return _original_init(self, *args, **kwargs)

                kwargs["docs_url"] = None
                _original_init(self, *args, **kwargs)

                self.mount(
                    "/static/swagger",
                    StaticFiles(directory=swagger_ui_path),
                    name="swagger",
                )

                @self.get(docs_path, include_in_schema=False)
                def _offline_docs():
                    return get_swagger_ui_html(
                        openapi_url=self.openapi_url,
                        title=self.title + " - Swagger UI",
                        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
                        swagger_css_url="/static/swagger/swagger-ui.css",
                    )

            FastAPI.__init__ = _init_with_local_docs
            FastAPI._offline_docs_patched = True
    except Exception:
        # 任何异常都不应阻止应用启动；失败时退回 FastAPI 默认行为
        pass
