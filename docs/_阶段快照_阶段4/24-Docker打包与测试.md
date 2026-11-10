# 第 24 章 Docker 打包与测试

> **节首信息条**｜对应课次 24 · 4 学时 · 实践｜前置：第 23 章的镜像、容器与 Dockerfile；第 7 章的后端结构；第 22 章的前端｜章末有质量评价量表、AI 了解性侧栏与本章提示页

上一章读懂了 Dockerfile，但还没有亲手构建。本章完成第一次完整打包：为后端与前端各写一个 Dockerfile，构建镜像，运行容器，用 `/health`、`/docs` 与页面验证。只做单服务，前后端联通留到下一章。

打包最容易卡住的地方不在 Dockerfile 语法，而在环境与路径：Docker 没启动、基础镜像拉不下来、`COPY` 路径写错、端口被占用、容器启动即退出。本章按“写文件 → 构建 → 运行 → 验证 → 排错”的顺序走一遍。

> 环境提示：本章的 `docker build`、`docker run` 需要 Docker 守护进程运行。教材编写环境的 Docker Desktop 未启动，因此涉及实际构建与运行的步骤标注为待核；命令语义与 Dockerfile 内容已按项目文件核对。读者执行前先确认 `docker info` 可用。

## 本章学习目标

读完第 24 章并完成实训后，你应该能：

1. 说明构建上下文与 `.dockerignore` 对镜像的影响。
2. 按“先依赖、后代码”的顺序写后端 Dockerfile，并利用缓存加速。
3. 构建、运行并验证后端镜像，能读取容器日志定位启动失败。
4. 为前端写 Dockerfile，正确设置启动参数与后端地址。
5. 识别“容器里的 127.0.0.1”问题，并做基础镜像体积优化。

## 前置知识卡

| # | 已有知识 | 回看位置 |
| --- | --- | --- |
| 1 | 本章依赖的前置内容 | 第 23 章的镜像、容器与 Dockerfile；第 7 章的后端结构；第 22 章的前端 |
| 2 | 上一章的核心结论 | 见上一章「本章小结」 |
| 3 | 本章实训/案例所需的环境与数据 | 见本章实训「二、课前准备」或章首导入 |

> 卡住时先回看，不必从头重读。

## 24.1 概念讲解

### 24.1.1 构建上下文：`docker build .` 里的点

`docker build -t duty-backend:1.0 .` 末尾的 `.` 是构建上下文，不是 Dockerfile 所在目录。Docker 会把上下文目录发给守护进程，`COPY` 的源路径都相对于这个上下文。

因此，构建命令要在项目根目录执行；`COPY requirements.txt .` 找的是上下文根部的 `requirements.txt`。上下文太大，构建会慢；`.dockerignore` 就是给上下文做减法。

### 24.1.2 后端 Dockerfile 的顺序

**代码 24-1-1** · Dockerfile 片段

```dockerfile
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim
WORKDIR /app
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "main.py"]
**代码 24-1-2** · 示例（文本）

```

| 顺序 | 指令 | 为什么放这里 |
| --- | --- | --- |
| 1 | `FROM` | 基础环境固定 |
| 2 | `WORKDIR` | 后续路径都在 `/app` |
| 3 | `COPY requirements.txt .` | 依赖清单变化少，先复制 |
| 4 | `RUN pip install` | 依赖层尽量复用 |
| 5 | `COPY . .` | 代码变化频繁，放最后 |
| 6 | `ENV` | 运行行为固定 |
| 7 | `EXPOSE` / `CMD` | 声明端口与启动方式 |

### 24.1.3 .dockerignore 的三项底线

**代码 24-1-3** · 示例（文本）

```text
__pycache__
*.pyc
.venv
venv
env
.env
*.log
*.sqlite3
.git
.pytest_cache
**代码 24-1-4** · 示例（文本）

```

三项底线：`.env` 不能进镜像（含密钥）；`venv/` 不能进镜像（本机虚拟环境）；`*.sqlite3` 与 `*.log` 不能进镜像（本机数据与日志）。再加 `.git/`、`__pycache__/`，上下文会小很多。

### 24.1.4 构建与缓存

**代码 24-1-5** · 命令（Bash）

```bash
cd duty
docker build -t duty-backend:1.0 .
docker images | grep duty-backend
**代码 24-1-6** · 示例（文本）

```

观察构建日志：每条 `RUN` / `COPY` 对应一步；第二次构建出现 `CACHED`；最后出现成功标记。改一行业务代码再构建，只有 `COPY . .` 及其后的层重建，依赖层命中缓存。

### 24.1.5 运行与验证

**代码 24-1-7** · 命令（Bash）

```bash
docker run -d --name duty-backend -p 8000:8000 duty-backend:1.0
docker ps
curl http://127.0.0.1:8000/health
**代码 24-1-8** · 示例（文本）

```

预期返回 `{"status":"healthy"}`。再看三处：浏览器打开 `/docs`；`docker logs duty-backend` 看启动日志；`docker exec -it duty-backend sh` 进入容器查看 `/app`。

| 参数 | 作用 |
| --- | --- |
| `-d` | 后台运行 |
| `--name` | 给容器起名，方便 logs/exec/rm |
| `-p 8000:8000` | 宿主机 8000 → 容器 8000 |
| `--rm` | 容器停止后自动删除（调试用） |

### 24.1.6 前端 Dockerfile 的三个启动参数

**代码 24-1-9** · Dockerfile 片段

```dockerfile
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim
WORKDIR /app
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8501
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
**代码 24-1-10** · 示例（文本）

```

| 参数 | 作用 | 不写会怎样 |
| --- | --- | --- |
| `--server.port=8501` | 指定端口 | 默认 8501，但写出来更明确 |
| `--server.address=0.0.0.0` | 监听所有网卡 | 只监听容器内回环，宿主机访问不到 |
| `--server.headless=true` | 不自动打开浏览器 | 容器里会尝试开浏览器，报错或卡住 |

### 24.1.7 容器里的 127.0.0.1 不是宿主机

前端页面能打开，但登录会失败。原因在 `duty_frontend/config.py`：

**代码 24-1-11** · 示例代码（Python）

```python
API_BASE_URL = os.getenv("DUTY_API_BASE_URL", "http://127.0.0.1:8000")
**代码 24-1-12** · 示例（文本）

```

这行代码在容器里执行时，`127.0.0.1` 指的是前端容器自己，不是宿主机，也不是后端容器。前端在找“自己身上的 8000 端口”，当然连不上。

本章只记录现象与原因，不解决；下一章用环境变量 `DUTY_API_BASE_URL` 与容器网络让前端找到后端。

### 24.1.8 镜像体积优化

**代码 24-1-13** · 命令（Bash）

```bash
docker images
docker history duty-backend:1.0
**代码 24-1-14** · 示例（文本）

```

优化顺序从易到难：用精简基础镜像（`slim`）；先依赖后代码；`pip install --no-cache-dir`；`.dockerignore` 排除无关文件；多阶段构建（构建阶段装工具，运行阶段只拷产物）。

先能跑，再优化。不要为了省几十 MB 删掉运行必需的文件，也不要为了“看起来小”把日志、数据库打进镜像。

### 24.1.9 常见构建与运行错误

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 拉取基础镜像失败 | 网络或镜像源不可用 | 用预拉取镜像；检查网络 |
| `COPY failed: no source files` | 构建上下文目录不对 | 确认在项目根目录执行，末尾的 `.` 不能漏 |
| `pip install` 超时 | 镜像源不可达 | 用课程提供的 pip 源 |
| 构建特别慢、上下文很大 | `venv/` 被打进上下文 | 检查 `.dockerignore` 是否生效 |
| 端口被占用 | 本机已有服务在 8000 运行 | 先停本机服务，或改用 `-p 8001:8000` |
| 容器启动即退出 | 启动命令报错 | `docker logs` 看堆栈 |
| `/health` 不通 | 服务没监听 `0.0.0.0` | 检查启动命令 |
| `docker exec` 进不去 | 容器已退出 | 先 `docker ps -a` 看状态 |

## 24.2 示范例题

#### 例 24-1：为后端写 Dockerfile【Bloom：应用】

**题目**：为 FastAPI 后端写一个 Dockerfile：使用 `python:3.12.9-slim`，工作目录 `/app`，安装 `requirements.txt`，复制代码，暴露 8000，启动 `python main.py`。说明为什么先复制依赖文件。

**解**：

**代码 24-2-1** · Dockerfile 片段

```dockerfile
FROM python:3.12.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "main.py"]
**代码 24-2-2** · 示例（文本）

```

先复制 `requirements.txt` 并安装依赖，是为了让依赖层在业务代码变化时仍命中缓存；`COPY . .` 放在最后，改代码只重建代码层。`--no-cache-dir` 避免把 pip 缓存打进镜像。

#### 例 24-2：诊断镜像体积【Bloom：分析】

**题目**：`docker history` 显示某镜像各层大小为：基础层 130 MB、依赖层 220 MB、代码层 15 MB、其他 5 MB。请指出体积主要来自哪里，并给出三条可行的优化建议。

**解**：

1. 体积主要来自依赖层（220 MB）与基础层（130 MB）。
2. 优化建议：换更精简的基础镜像（如 `slim`，已经使用则检查是否引入了编译工具）；安装依赖时加 `--no-cache-dir`，避免缓存层；把只在构建阶段需要的工具放到多阶段构建的构建阶段，运行阶段只拷产物；用 `.dockerignore` 排除虚拟环境、日志、数据库等无关文件。
3. 注意：不要为了减小体积删掉运行必需的系统库或依赖；优化后要重新运行 `/health` 与核心接口，确认功能未受影响。

## 24.3 引导练习

#### 例 24-3（引导练习）：用多阶段构建减小体积【Bloom：应用】

**题目**：某项目构建时需要编译工具，运行时不需。请用多阶段构建写一个骨架，说明两个阶段各做什么。

#### 例 24-4（引导练习）：补齐 .dockerignore【Bloom：应用】

**题目**：某项目的 `.dockerignore` 只写了 `__pycache__`。请补全至少五类应排除内容，并说明不排除的后果。

## 24.4 独立习题

#### 习题 24-1【Bloom：应用】

**题目**：为前端 Streamlit 应用写 Dockerfile：暴露 8501，启动时指定端口、监听 `0.0.0.0`、开启 headless。说明三个启动参数各自的作用。

#### 习题 24-2【Bloom：应用】

**题目**：写出构建后端镜像 `duty-backend:1.0`、后台运行并映射 8000 端口、查看容器状态与 `/health` 的完整命令序列。

#### 习题 24-3【Bloom：分析】

**题目**：某同学改了业务代码后重新构建，发现依赖层也重建了。请分析可能原因，并给出修正方法。

#### 习题 24-4【Bloom：评价】（开放题）

**题目**：有人主张“镜像越小越好”，为此删除了容器内的调试工具与部分系统库；也有人主张“能跑优先，体积其次”。请评价两种做法，并给出你的优化原则。

## ◆ 实训 24-1：Docker 打包与测试（对应课次 24 · 4 学时）

### 一、任务目标与验收

| 目标 | 验收标志 |
| --- | --- |
| 后端镜像可构建 | `docker build` 成功，镜像可运行 |
| 缓存有效 | 只改代码时依赖层不重建 |
| 运行验证 | 容器内服务可访问、日志正常 |
| 前端镜像可用 | 启动参数与后端地址正确 |
| 体积有优化 | 能说明至少两项优化 |

### 二、课前准备

- Docker 已安装并可运行
- 第 22 章的前后端代码
- 一份 `.dockerignore` 草稿

### 三、操作步骤

1. **写后端 Dockerfile**
   - 做什么：写后端 Dockerfile
   - 操作：`先复制依赖清单装依赖，再复制代码`
   - 预期输出：→ 构建成功、缓存可复用
   - 做错会看到什么：先复制全部代码再装依赖；每次改代码都重建依赖
2. **构建与运行**
   - 做什么：构建与运行
   - 操作：`docker build`、`docker run -p`，查看日志
   - 预期输出：→ 容器可访问、日志无异常
   - 做错会看到什么：容器退出；用 `docker logs` 看最后几行
3. **写前端 Dockerfile**
   - 做什么：写前端 Dockerfile
   - 操作：`设置启动参数与后端地址`
   - 预期输出：→ 前端能访问后端
   - 做错会看到什么：容器内写 `127.0.0.1`；改为服务名或宿主机地址
4. **优化体积**
   - 做什么：优化体积
   - 操作：`换 slim/alpine 基础镜像、清理缓存`
   - 预期输出：→ 体积下降且功能不变
   - 做错会看到什么：为省体积删掉运行依赖；回归验证

### 四、排错清单

| 现象 | 先查什么 |
| --- | --- |
| 构建很慢 | 构建上下文过大或缓存顺序错 |
| 容器启动即退出 | 启动命令错误、端口不匹配 |
| 前端请求失败 | 容器内地址、跨域、网络 |
| 镜像过大 | 基础镜像、缓存文件、无用依赖 |

### 五、提交与验收

提交两个 Dockerfile、构建与运行记录、体积对比；验收按“可构建运行”“缓存与优化”“前端联调”三项判定。

### 六、课后扩展

- 用多阶段构建减小前端镜像
- 给镜像打版本标签
- 写一份构建失败排查清单

### 七、回链

- 第 23 章 23.1.4–23.1.8；第 7 章后端结构；第 22 章前端联调；本章 24.1.1–24.1.9

## 本章小结

**核心结论**：

1. `docker build .` 的点是构建上下文；`COPY` 的源路径相对于上下文，不是 Dockerfile。
2. 后端 Dockerfile 顺序：基础镜像 → 工作目录 → 依赖 → 代码 → 环境变量 → 端口 → 启动命令；变化少的放前面。
3. `.dockerignore` 守住三条底线：`.env`、虚拟环境、数据库与日志都不进镜像。
4. 运行用 `-d --name -p`；验证用 `/health`、`/docs`、`docker logs`、`docker exec`；容器里的 `127.0.0.1` 指容器自己。
5. 体积优化按“slim → 先依赖后代码 → no-cache-dir → .dockerignore → 多阶段”的顺序；先能跑再优化，优化后必须回归。

**学完本章，你可以体会到**：镜像构建的每个顺序都影响速度与可复现性，容器化是把“环境”也当成代码来管理。
**自检**：回到章首的学习目标，逐条问自己做到了没有——

- [ ] 说明构建上下文与 `.dockerignore` 对镜像的影响。 → 回看 24.1.1–24.1.2，自测：习题 24-1
- [ ] 按“先依赖、后代码”的顺序写后端 Dockerfile，并利用缓存加速。 → 回看 24.1.3–24.1.4，自测：习题 24-1
- [ ] 构建、运行并验证后端镜像，能读取容器日志定位启动失败。 → 回看 24.1.5，自测：习题 24-1
- [ ] 为前端写 Dockerfile，正确设置启动参数与后端地址。 → 回看 24.1.6–24.1.7，自测：习题 24-1
- [ ] 识别“容器里的 127.0.0.1”问题，并做基础镜像体积优化。 → 回看 24.1.8–24.1.9，自测：习题 24-1

**下一章预告**：两个容器各自能跑，但前端还找不到后端。下一章用环境变量与 compose 把前后端连起来，完成整套部署。

## 换场景总表

| 本章场景 | 换成其他场景 |
| --- | --- |
| FastAPI 后端镜像 | 换成 Flask/Django/Node 服务，顺序与缓存原则不变 |
| Streamlit 前端镜像 | 换成 Nginx 静态站点，启动参数与地址配置同理 |
| SQLite | 换成 PostgreSQL 容器，网络与卷的配置问题类似 |

## 章末质量评价量表（本实训）

| 维度 | 分档描述 | 权重 |
| --- | --- | ---: |
| 可构建运行 | 两个镜像均可用 | 30% |
| 缓存与顺序 | 依赖层复用有效 | 20% |
| 联调正确 | 前端能访问后端 | 25% |
| 优化与排错 | 体积优化、日志定位 | 25% |
| **合计** | | **100%** |

评价方式：自评 30% + 互评 30% + 师评 40%。

**一票否决**：涉密信息未脱敏、安全漏洞不处理、提交记录造假——出现任一项，本实训记不通过。

## AI 侧栏（了解即可）

> AI 生成的 Dockerfile 常把 `COPY . .` 放在安装依赖之前，缓存全失效；也常在容器里用 `127.0.0.1` 指向后端。审查时先看指令顺序，再看地址。

## 本章提示页

> 先自己做，卡住了再看。提示按“方向 → 关键步骤 → 完整解答”排列。

**例 24-3（引导练习）：用多阶段构建减小体积【Bloom：应用】**

**提示 1（方向）**

第一阶段用完整镜像装依赖并构建；第二阶段用 slim 镜像，只复制构建产物。

**提示 2（关键步骤）**

用 `FROM ... AS builder` 命名构建阶段；运行阶段 `COPY --from=builder /app /app`。

**完整解答**

**代码 24-4-1** · Dockerfile 片段

```dockerfile
FROM python:3.12.9 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY . .

FROM python:3.12.9-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /app /app
EXPOSE 8000
CMD ["python", "main.py"]
**代码 24-4-2** · 示例（文本）

```

构建阶段装依赖与编译工具；运行阶段只保留运行所需文件，编译工具不进入最终镜像。

**例 24-4（引导练习）：补齐 .dockerignore【Bloom：应用】**

**提示 1（方向）**

从“密钥、虚拟环境、运行产物、版本库、缓存”五类想。

**提示 2（关键步骤）**

`.env`、`venv/`、`*.log`、`*.sqlite3`、`.git/`、`.pytest_cache/`。

**完整解答**

**代码 24-4-3** · 示例（文本）

```text
__pycache__
*.pyc
.venv
venv
env
.env
*.log
*.sqlite3
.git
.pytest_cache
**代码 24-4-4** · 示例（文本）

```

不排除的后果：`.env` 泄露密钥；`venv/` 让上下文与镜像膨胀；日志与数据库把本机运行产物带进镜像；`.git/` 增加体积并可能泄露历史信息；缓存目录让构建变慢。