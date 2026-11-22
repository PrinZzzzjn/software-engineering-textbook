# 内网环境课程依赖与离线安装清单（Linux ARM64 授课机）

编制日期：2026-11-20。适用对象：需要在无公网的内网机房独立安装课程教学环境的教师/管理员。

## 1. 结论速览

- 本课程前后端**都是 Python**，不需要 Node.js、npm、Vue、React。
- 解释器统一用 **Python 3.12**（教材 Dockerfile 与示例为 `python:3.12.9-slim`）；数据库用 **SQLite**，Python 标准库自带，不装 MySQL/PostgreSQL。
- 认证只用标准库 `hashlib` + `secrets`，**不需要** `python-jose`、`passlib`、`bcrypt`、`SECRET_KEY`。
- **授课机为 Linux ARM64（aarch64）**：使用 `requirements.linux-arm64.lock.txt`；Windows x64、Linux x86_64 锁文件保留给其他机房。
- pip 依赖共 **55–56 个包**（含传递依赖；Linux/ARM64 多一个 `uvloop`），顶层只有 9 个：后端 4、测试 2、前端 3；另含 1 个可选的 Swagger UI 离线资源包。
- 目标机必须已有 **Python 3.12**（`python3.12 -V`）。只有 3.10/3.11 时先离线装 3.12，否则 cp312 的二进制轮子全部不匹配。
- 系统级工具：`Git`（第 5 章）、现代浏览器（看 `/docs` 与 8501 页面）、`Docker Engine + Compose 插件`（仅第 21-24 章）。
- `tools/` 下的教材校验脚本只用 Python 标准库，无需额外依赖。

## 2. 顶层依赖及来源

| 分组 | 包 | 版本 | 来源与用途 |
| --- | --- | --- | --- |
| 后端运行 | `fastapi` | 0.165.0 | `项目参考/duty-simplified/requirements.txt`；第 3 章起框架与接口 |
| 后端运行 | `uvicorn[standard]` | 0.54.0 | 同上；启动服务，extras 含 httptools/watchfiles/websockets 等 |
| 后端运行 | `sqlalchemy` | 2.1.9 | 同上；第 6 章起数据层 |
| 后端运行 | `pydantic` | 2.14.4 | 同上；输入/输出模型校验（课程只用 v2 API） |
| 测试 | `pytest` | 9.2.0 | 第 12 章 `pip install pytest httpx` |
| 测试 | `httpx` | 0.28.1 | 第 12 章 `TestClient` 发请求 |
| 前端 | `streamlit` | 1.67.0（约束 `>=1.50,<2`） | `项目参考/duty_frontend/requirements.txt`；第 14 章起 |
| 前端 | `requests` | 2.34.2（约束 `>=2.31`） | 前端调用后端接口 |
| 前端 | `pandas` | 2.3.x（约束 `>=2.0,<3`） | 列表/统计页数据处理；**不要升到 3.x**，课程代码按 2.x 验证 |
| 可选 | `swagger-ui-bundle` | 1.1.0 | 内网把 `/docs` 的静态资源落到本地，见第 6 节 |

不需要安装：Node/npm、MySQL/PostgreSQL、Redis、JWT/passlib 系列、`alembic`、`pydantic-settings`（这些只出现在历史工程 `duty-historical/`，现行课程不用）。

## 3. 离线安装：wheelhouse 方案（推荐）

### 3.1 在能上网的准备机上下载 wheel

准备机只需有 **Python 3.12 与 pip**；目标架构由 `--platform` 指定，因此可以在 x86 机器上为 ARM64 下载 wheel。下载操作不安装包，只把 `.whl` 存到目录。

**Linux ARM64（授课机；先在目标机执行 `uname -m`，预期输出 `aarch64`）：**

```bash
pip download --only-binary=:all: --python-version 3.12 --implementation cp --abi cp312 --platform manylinux2014_aarch64 -d wheelhouse-arm64 -r requirements.linux-arm64.lock.txt
```

**Linux x86_64（其他机房）：**

```bash
pip download --only-binary=:all: --python-version 3.12 --implementation cp --abi cp312 --platform manylinux2014_x86_64 -d wheelhouse-linux -r requirements.linux-x64.lock.txt
```

**Windows x64：**

```bat
pip download --only-binary=:all: --python-version 3.12 --implementation cp --abi cp312 --platform win_amd64 -d wheelhouse-win -r requirements.win-x64.lock.txt
```

说明：

- ARM64 轮子按 `manylinux2014_aarch64`（glibc >= 2.17）选取；目标机用 `ldd --version` 确认 glibc 版本。若目标是 Alpine ARM（musl），平台要改为 `musllinux_1_2_aarch64`，本清单未覆盖该组合，需要单独解析。
- 锁定文件已固定版本；Linux/ARM64 锁文件比 Windows 多 `uvloop`，这是 `uvicorn[standard]` 在非 Windows 平台的依赖。
- 把 `wheelhouse-arm64/` 连同本目录的 requirements 文件一起拷入内网。

### 3.2 在内网目标机安装

Windows（`*.lock.txt` 与 wheelhouse 放在同一目录）：

```bat
python -m venv venv
venv\Scripts\activate
pip install --no-index --find-links=./wheelhouse-win -r requirements.win-x64.lock.txt
```

Linux ARM64（授课机）：

```bash
uname -m                      # 预期 aarch64
python3.12 -V                 # 预期 Python 3.12.x
python3.12 -m venv venv
source venv/bin/activate
pip install --no-index --find-links=./wheelhouse-arm64 -r requirements.linux-arm64.lock.txt
```

Linux x86_64（其他机房）把最后一行换成：

```bash
pip install --no-index --find-links=./wheelhouse-linux -r requirements.linux-x64.lock.txt
```

`--no-index` 保证 pip 完全不访问公网；`--find-links` 指向本地 wheel 目录。不要用教材里的 `pip install -r requirements.txt` 原命令，内网必须加这两个参数。

### 3.3 验证安装

```bash
python -c "import fastapi,uvicorn,sqlalchemy,pydantic,pytest,httpx,streamlit,pandas,requests; print('deps ok')"
cd 项目参考/duty-simplified
python -m pytest tests/test_smoke.py -q        # 预期 3 passed
uvicorn main:app --reload --port 8000          # 浏览器访问 /health、/docs
cd ../duty_frontend
streamlit run app.py --server.headless=true    # 浏览器访问 http://127.0.0.1:8501
```

前端默认请求 `http://127.0.0.1:8000`；若后端在别的机器，设置环境变量 `DUTY_API_BASE_URL=http://<后端IP>:8000`。

## 4. 另一种方案：直接搬运环境

同型号、同系统、同 Python 版本、且虚拟环境路径完全一致的机器，可以把激活后的 `venv/` 整个压缩搬过去。跨机器、跨路径时激活脚本里的绝对路径会失效，优先用第 3 节的 wheelhouse 重建。

## 5. Docker 章节（第 21-24 章）的离线准备

### 5.1 软件本身

内网需预置 Docker Engine（或 Docker Desktop）与 Compose 插件，验收命令：

```bash
docker version
docker compose version
```

### 5.2 基础镜像

两个参考 Dockerfile 都使用 `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim`，教材示例还用 `python:3.12-slim`。授课机是 ARM64，镜像也必须是 arm64 变体；`docker save` 出来的 tar 与架构绑定，x86 镜像搬到 ARM 机上无法运行。

在能联网的 ARM 机器上（或支持 `--platform` 的环境）：

```bash
docker pull --platform linux/arm64 swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim
docker pull --platform linux/arm64 python:3.12-slim
docker image inspect --format '{{.Architecture}}' swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim   # 预期 arm64
docker save -o python-images-arm64.tar swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim python:3.12-slim
```

若华为镜像没有 arm64 变体（`docker pull` 报 `no matching manifest`），把两个 Dockerfile 的 `FROM` 改为官方多架构镜像，再按上面的命令拉取/导出：

```dockerfile
FROM python:3.12.9-slim
```

把 tar 拷入内网后 `docker load -i python-images-arm64.tar`，并在 ARM 机上用 `docker image inspect --format '{{.Architecture}}' <镜像>` 复核。

### 5.3 更省事：直接搬运构建好的业务镜像

在联网机 build 后导出：

```bash
docker build -t duty-backend:1.0 ./项目参考/duty-simplified
docker build -t duty-frontend:1.0 ./项目参考/duty_frontend
docker save -o duty-images.tar duty-backend:1.0 duty-frontend:1.0
```

如果准备机是 x86、目标机是 ARM64，直接 `docker build` 会产出 x86 镜像；要用 buildx 交叉构建：

```bash
docker buildx build --platform linux/arm64 -t duty-backend:1.0 --load ./项目参考/duty-simplified
docker buildx build --platform linux/arm64 -t duty-frontend:1.0 --load ./项目参考/duty_frontend
docker save -o duty-images-arm64.tar duty-backend:1.0 duty-frontend:1.0
```

`--load` 只支持单平台；首次使用需 `docker buildx create --use`，并确保 QEMU 模拟可用，构建会明显变慢。更稳的做法是在 ARM 机器上直接 build。

内网 `docker load -i duty-images-arm64.tar`（ARM 机）或 `docker load -i duty-images.tar`（x86 机），然后把 `项目参考/docker-compose.yml` 里两个服务的 `build: context: ...` 改为 `image: duty-backend:1.0` / `image: duty-frontend:1.0`，用 `docker compose up -d`（不要带 `--build`）启动。端口、环境变量、健康检查、依赖顺序都不变。

### 5.4 若必须在内网构建镜像

两个 Dockerfile 目前都写死了公网 pip 镜像：

```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir -r requirements.txt
```

内网要删掉 `pip config` 那行，并把 **ARM64** wheelhouse（`wheelhouse-arm64/`）放进各项目的 `wheelhouse/` 目录；构建阶段运行在 arm64 上，不能放 x86_64 的轮子：

```dockerfile
COPY wheelhouse/ /wheels/
RUN pip install --no-index --find-links=/wheels -r requirements.txt
```

`.dockerignore` 里不要排除 `wheelhouse/`。构建用 `docker compose build`（已加载本地基础镜像时不会联网）。

## 6. 内网两个容易踩的坑

1. **`/docs` 页面空白**：FastAPI 默认从公网 CDN 加载 Swagger UI 的 JS/CSS。`/openapi.json` 不受影响。要本地化，在 `main.py` 创建应用处改为：

   ```python
   from fastapi import FastAPI
   from fastapi.openapi.docs import get_swagger_ui_html
   from fastapi.staticfiles import StaticFiles
   from swagger_ui_bundle import swagger_ui_path

   app = FastAPI(title="执勤电子年鉴", docs_url=None, redoc_url=None)
   app.mount("/static/swagger", StaticFiles(directory=swagger_ui_path), name="swagger")

   @app.get("/docs", include_in_schema=False)
   def local_docs():
       return get_swagger_ui_html(
           openapi_url=app.openapi_url,
           title=app.title + " - Swagger UI",
           swagger_js_url="/static/swagger/swagger-ui-bundle.js",
           swagger_css_url="/static/swagger/swagger-ui.css",
       )
   ```

   其余路由照常挂载。`swagger-ui-bundle` 已列入锁定清单，会随 wheelhouse 一起下载。

2. **测试输出有一条告警**：锁定版本下 `starlette 1.10` 的 `TestClient` 会提示 `httpx` 弃用告警，但 `test_smoke.py` 仍是 3 passed，不影响教学。若必须消除，可另测组合 `fastapi==0.130.0` + `starlette<1`（已验证 3 passed，但会换出另一条 anyio 告警），不建议为此改动教材正文。

## 7. 文件说明

- `requirements.course.txt`：按用途分组的顶层依赖，便于阅读和采购。
- `requirements.linux-arm64.lock.txt`：Linux ARM64（aarch64）+ Python 3.12 的完整锁定版本（56 个包，含 `uvloop`），**授课机使用**。
- `requirements.linux-x64.lock.txt`：Linux x86_64 + Python 3.12 的完整锁定版本（56 个包，含 `uvloop`），其他 x86_64 机房使用。
- `requirements.win-x64.lock.txt`：Windows x64 + Python 3.12 的完整锁定版本（55 个包）。

锁定版本于 2026-11-20 解析；后端 4 个运行依赖 + 测试 2 个依赖已在 x86_64 临时虚拟环境按锁定版本安装，并跑通 `项目参考/duty-simplified/tests/test_smoke.py`（3 passed）。ARM64 已完成解析与逐包轮子可用性检查（含 `numpy/pandas/pyarrow/pillow/pydantic-core/uvloop` 的 `manylinux2014_aarch64` 轮子），尚未在 ARM 实机复跑。
