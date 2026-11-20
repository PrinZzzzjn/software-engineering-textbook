"""前端配置：集中管理后端地址与请求参数。

教学要点：
- 后端地址不要硬编码到每个页面，统一放在这里；
- 用环境变量覆盖，方便从"本机开发"切换到"Docker 部署"；
- 分页大小、超时时间也集中管理，改一处即可全局生效。
"""

import os

# 后端服务地址。本地开发默认 127.0.0.1:8000；部署到容器时用环境变量覆盖。
API_BASE_URL = os.getenv("DUTY_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# 后端业务接口不设版本前缀，资源路径直接挂在根下（见 duty-simplified/main.py）
API_PREFIX = ""

# 单次请求超时时间（秒）
REQUEST_TIMEOUT = 10

# 列表页默认每页条数
DEFAULT_PAGE_SIZE = 10
