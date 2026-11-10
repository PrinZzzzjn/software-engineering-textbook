# 课次24：Docker打包与测试——把 duty 和前端装进镜像

## 一、课次基本信息

| 项目 | 内容 |
|---|---|
| 所属专题 | 专题四：软件部署与系统交付 |
| 学时 | 4 学时（实践，约 180 分钟） |
| 教材对应 | 第18章 容器化基础（18.3–18.4） |
| 主线案例 | `duty` 后端与 `duty_frontend` 前端各构建一个镜像 |
| 教学形态 | 教师示范 + 学生动手构建 + 容器验证 + 故障排查 |
| 教学定位 | **第一次完整打包**：写 Dockerfile → 构建 → 运行 → 验证；只做单服务，**前后端联通在课次25** |

## 二、教学目标

**知识与技能**

- 能读懂并编写后端 Dockerfile：`FROM`、`WORKDIR`、`COPY`、`RUN`、`ENV`、`EXPOSE`、`CMD`。
- 能编写 `.dockerignore`，排除虚拟环境、密钥、日志、数据库文件。
- 能用 `docker build` 构建镜像，并读懂构建日志与缓存命中。
- 能用 `docker run -d -p` 运行容器，并用 `curl`、`docker logs`、`docker exec` 验证。
- 能为 `duty_frontend` 编写 Dockerfile，处理 Streamlit 的 8501 端口、`0.0.0.0` 与 `headless` 参数。
- 能说清镜像体积与构建缓存优化的基本思路。

**过程与方法**

- 经历"写 Dockerfile → 构建 → 运行 → 验证 → 排错"的完整打包过程。
- 学会用构建日志和容器日志定位问题。

**情感态度与价值观**

- 养成"镜像可复现"的意识：同一个镜像，谁跑都一样。
- 建立"不把密钥、垃圾文件打进镜像"的底线意识。

## 教学内容

> 对应教学计划：专题四基本内容第 2 条"Docker打包与测试"。

1. **构建上下文与 `.dockerignore`**：`docker build .` 的 `.` 是什么。
2. **后端 Dockerfile 的结构**：基础镜像、工作目录、依赖、代码、启动。
3. **镜像构建**：`docker build`、镜像标签、分层缓存。
4. **容器运行与验证**：`docker run -d -p`、`/health`、`/docs`、`docker logs`。
5. **前端 Dockerfile**：Streamlit 启动参数、8501 端口。
6. **镜像体积与缓存优化**：slim 基础镜像、先依赖后代码、`--no-cache-dir`、多阶段构建（概念）。
7. **常见构建与运行错误**：拉取失败、路径错、端口占用、容器启动即退出。

## 三、重点与难点

**重点**

- 后端、前端 Dockerfile 的编写。
- 镜像构建与容器运行验证。
- `.dockerignore` 与构建上下文。

**难点**

- `COPY` 的源路径相对于构建上下文，不是相对于 Dockerfile。
- 缓存为什么失效、什么时候命中。
- 容器内 `127.0.0.1` 指向容器自己，不是宿主机。

## 四、学情分析与教学策略

上节课听懂了概念，但没有亲手构建。常见卡点不在"写 Dockerfile"，而在环境与路径：Docker 没启动、镜像拉不下来、`COPY` 路径错、端口被占用、容器启动即退出。

策略：

- **先照抄，再删改**：以 `duty/Dockerfile` 为模板，先构建成功，再解释每一行；
- **每步给验收命令**：构建完看 `docker images`，运行完看 `docker ps` 和 `/health`；
- **先后端、后前端**：后端链路简单，先建立信心；
- **主动制造失败**：改错路径、占用端口，让学生看到真实报错；
- **不要求优化到位**：体积优化讲思路，课内只做一次对比。

## 五、教学准备

- Docker 可运行；预拉取 `python:3.12.9-slim`（或项目同款基础镜像）。
- `duty`、`duty_frontend` 完整代码；教师提前完整构建一遍。
- 验收命令清单（`/health`、`/docs`、`http://127.0.0.1:8501`）。
- 常见错误清单；端口 8000、8501 空闲。
- 数据目录、日志目录说明；测试账号 `admin/admin123`。

## 六、教学过程

### 环节1：导入与任务说明（10 分钟）

**教师演示**

```bash
docker images
docker ps
```

> 课次23 看的是别人的镜像。今天把自己写的 `duty` 和 `duty_frontend` 装进去。

**任务**

1. 构建后端镜像 `duty-backend:1.0`，运行后 `/health` 返回 `{"status":"healthy"}`；
2. 构建前端镜像 `duty-frontend:1.0`，运行后浏览器能打开 8501 页面；
3. 写清两个 `.dockerignore`；
4. 记录一次构建失败和一次修复。

**验收标准**

- `docker images` 能看到两个镜像；
- 两个容器处于 `Up` 状态；
- `curl http://127.0.0.1:8000/health` 返回 healthy；
- 浏览器能打开 `http://127.0.0.1:8501`。

---

### 环节2：构建环境检查（10 分钟）

**学生自查**

```bash
docker version
docker info
docker compose version
```

**检查四件事**

| 检查项 | 命令/方法 | 不通过的表现 |
|---|---|---|
| Docker 是否启动 | `docker info` | `Cannot connect to the Docker daemon` |
| 基础镜像是否可用 | `docker images` | 构建时拉取超时 |
| 端口是否被占用 | `netstat -ano \| findstr :8000`（cmd）或 `netstat -ano \| grep :8000`（Git Bash） | 容器启动失败或访问到别的服务 |
| 磁盘空间 | `docker system df` | 构建中途失败 |

**强调**

> 构建失败先别改 Dockerfile，先确认 Docker 在运行、镜像拉得到、端口没被占。

---

### 环节3：后端 Dockerfile 与 `.dockerignore`（30 分钟）

**教师投影 `duty/Dockerfile`，逐段讲**

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
```

**讲清顺序**

| 顺序 | 指令 | 为什么放这里 |
|---|---|---|
| 1 | `FROM` | 基础环境固定 |
| 2 | `WORKDIR` | 后续路径都在 `/app` |
| 3 | `COPY requirements.txt .` | 依赖清单变化少，先复制 |
| 4 | `RUN pip install` | 依赖层尽量复用 |
| 5 | `COPY . .` | 代码变化频繁，放最后 |
| 6 | `ENV` | 运行行为固定 |
| 7 | `EXPOSE` / `CMD` | 声明端口与启动方式 |

**学生编写 `.dockerignore`**

```text
__pycache__
*.pyc
*.pyo
*.pyd
.venv
venv
env
.env
*.log
*.sqlite3
.git
.gitignore
.idea
.vscode
.pytest_cache
```

**检查三件事**

- `.env` 有没有排除？——密钥不能进镜像；
- `venv/` 有没有排除？——本机虚拟环境不能进镜像；
- `*.sqlite3`、`*.log` 有没有排除？——本机数据和日志不能进镜像。

**强调**

> `COPY . .` 里的 `.` 是构建上下文，不是 Dockerfile 所在目录。
> `.dockerignore` 就是给这个 `.` 做减法。

---

### 环节4：构建后端镜像（30 分钟）

**学生动手**

```bash
cd duty
docker build -t duty-backend:1.0 .
docker images | grep duty-backend
```

**观察构建日志**

- 每一条 `RUN` / `COPY` 对应一步；
- 第二次构建出现 `CACHED`；
- 最后出现 `Successfully tagged duty-backend:1.0`。

**演示缓存**

```bash
docker build -t duty-backend:1.1 .
# 改一行业务代码后
docker build -t duty-backend:1.2 .
```

> 第一次全量；第二次全部命中；改代码后只有 `COPY . .` 及其后的层重建。

**常见错误**

| 现象 | 原因 | 处理 |
|---|---|---|
| 拉取基础镜像失败 | 网络或镜像源不可用 | 用预拉取镜像；检查网络 |
| `COPY failed: no source files` | 构建上下文目录不对 | 确认在 `duty/` 下执行，末尾的 `.` 不能漏 |
| `pip install` 超时 | 镜像源不可达 | 用课程提供的 pip 源 |
| 构建特别慢、上下文很大 | `venv/` 被打进上下文 | 检查 `.dockerignore` 是否生效 |
| `docker build` 报权限错误 | Docker 未启动或无权限 | 启动 Docker Desktop |

**学生任务（10 分钟）**

- 构建成功并截图 `docker images`；
- 故意把 `COPY requirements.txt .` 改成错误文件名，观察报错并改回。

---

### 环节5：运行与验证后端容器（30 分钟）

**教师演示**

```bash
docker run -d --name duty-backend -p 8000:8000 duty-backend:1.0
docker ps
curl http://127.0.0.1:8000/health
```

**预期**

```text
{"status":"healthy"}
```

**再看三处**

```bash
# 1. 接口文档
# 浏览器打开 http://127.0.0.1:8000/docs

# 2. 容器日志
docker logs duty-backend

# 3. 进入容器
docker exec -it duty-backend sh
ls -la /app
exit
```

**讲清参数**

| 参数 | 作用 |
|---|---|
| `-d` | 后台运行 |
| `--name` | 给容器起名字，方便 logs/exec/rm |
| `-p 8000:8000` | 宿主机 8000 → 容器 8000 |
| `--rm` | 容器停止后自动删除（调试时用） |

**常见错误**

| 现象 | 原因 | 处理 |
|---|---|---|
| 端口被占用 | 本机已有 duty 在 8000 运行 | 先停本机服务，或改用 `-p 8001:8000` |
| 容器启动即退出 | 启动命令报错 | `docker logs duty-backend` 看堆栈 |
| `/health` 不通 | 服务没监听 `0.0.0.0` | 检查 `main.py` 的 `uvicorn.run` |
| `docker exec` 进不去 | 容器已退出 | 先 `docker ps -a` 看状态 |

**强调**

> `-p 8000:8000` 左边是宿主机、右边是容器。
> 浏览器访问的是宿主机端口；容器内部只认自己的端口。

**学生任务（15 分钟）**

- 自己运行容器，截图 `/health` 和 `/docs`；
- 用 `-p 8001:8000` 再起一个容器（改个名字），验证两个容器可以同时存在；
- 用 `docker logs` 找出启动时的第一条日志。

---

### 环节6：前端 Dockerfile、构建与运行（40 分钟）

**教师投影 `duty_frontend/Dockerfile`**

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
```

**讲清三个启动参数**

| 参数 | 作用 | 不写会怎样 |
|---|---|---|
| `--server.port=8501` | 指定端口 | 默认 8501，但写出来更明确 |
| `--server.address=0.0.0.0` | 监听所有网卡 | 只监听容器内回环，宿主机访问不到 |
| `--server.headless=true` | 不自动打开浏览器 | 容器里会尝试开浏览器，报错或卡住 |

**学生动手**

```bash
cd duty_frontend
docker build -t duty-frontend:1.0 .
docker run -d --name duty-frontend -p 8501:8501 duty-frontend:1.0
docker ps
```

**浏览器打开 `http://127.0.0.1:8501`**

页面应该能打开。尝试登录，会出现**登录失败**。

**教师不马上解决，先让学生找原因**

> 打开 `duty_frontend/config.py`，看默认后端地址是什么。

```python
API_BASE_URL = os.getenv("DUTY_API_BASE_URL", "http://127.0.0.1:8000")
```

**讲清原因**

> 这行代码在容器里执行时，`127.0.0.1` 指的是 **前端容器自己**，不是宿主机，更不是后端容器。
> 所以前端在找"自己身上的 8000 端口"，当然连不上。

**明确边界**

> 这个问题今天不解决。课次25 用环境变量 `DUTY_API_BASE_URL` 和容器网络，让前端找到后端。
> 现在只需要记住现象和原因。

**学生任务**

- 构建前端镜像并打开页面；
- 记录登录失败的现象，写出你认为的原因（一句话）；
- 用 `docker logs duty-frontend` 看有没有报错。

---

### 环节7：镜像体积与优化（15 分钟）

**看体积**

```bash
docker images
docker history duty-backend:1.0
```

**优化顺序（从易到难）**

| 手段 | 做法 | 效果 |
|---|---|---|
| 用精简基础镜像 | `python:3.12.9-slim` | 去掉编译工具与文档 |
| 先依赖后代码 | `COPY requirements.txt` 在前 | 改代码不重装依赖 |
| 不装缓存 | `pip install --no-cache-dir` | 少一层 pip 缓存 |
| 排除无关文件 | `.dockerignore` | 上下文与镜像都变小 |
| 多阶段构建 | 构建阶段装工具，运行阶段只拷产物 | 体积明显下降（概念，课内不展开） |

**强调**

> 先能跑，再优化。不要为了省几十 MB 删掉运行必需的文件；
> 也不要为了"看起来小"把日志、数据库打进镜像。

---

### 环节8：小结、验收与作业（15 分钟）

**验收清单（学生逐项打勾）**

- [ ] `duty-backend:1.0` 镜像存在；
- [ ] `duty-frontend:1.0` 镜像存在；
- [ ] 两个容器都是 `Up`；
- [ ] `/health` 返回 healthy；
- [ ] `/docs` 能打开；
- [ ] 8501 页面能打开；
- [ ] 能解释前端登录失败的原因；
- [ ] `.dockerignore` 排除了 `.env`、`venv`、数据库文件。

**教师总结**

> 今天完成两件事：把后端装进镜像、把前端装进镜像。
>
> 三个关键点：`COPY` 的顺序决定缓存；`.dockerignore` 决定什么不进镜像；
> 容器里的 `127.0.0.1` 不是宿主机。

**布置作业**

1. 提交两个 Dockerfile、两个 `.dockerignore`。
2. 提交 `docker images` 截图、`/health` 截图、前端页面截图。
3. 写一段话解释"为什么前端容器登录失败"，不超过 100 字。
4. 预习课次25：环境变量、端口映射、容器网络。

## 七、板书设计

```text
一、构建上下文
   docker build -t 名字:版本 .
                              ↑ 这个点 = 上下文目录
   .dockerignore 给上下文做减法
   排除：.env / venv / *.log / *.sqlite3 / .git

二、后端 Dockerfile
   FROM → WORKDIR → COPY requirements → RUN pip → COPY . . → ENV → EXPOSE → CMD
   顺序原则：少变的在前，多变的在后

三、构建与运行
   docker build -t duty-backend:1.0 .
   docker run -d --name duty-backend -p 8000:8000 duty-backend:1.0
   docker logs / docker exec / docker ps

四、前端 Dockerfile
   EXPOSE 8501
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
   127.0.0.1 在容器里 = 容器自己 → 登录失败 → 课次25 解决

五、优化
   slim / 先依赖后代码 / --no-cache-dir / .dockerignore / 多阶段（了解）
```

## 八、作业与课后任务

- 必做：两个 Dockerfile、两个 `.dockerignore`、三张截图、一段失败原因说明。
- 选做：用 `-p 8001:8000` 再起一个后端容器，比较两个容器的日志。
- 预习：课次25 的 `-e`、`--network`、`-v` 三个参数分别解决什么问题。

## 九、评价与反馈

- 验收：两个镜像能构建、两个容器能运行、后端健康检查通过、前端页面能打开。
- 过程：`.dockerignore` 是否排除敏感文件；是否理解 `COPY` 顺序；能否从日志读出失败原因。
- 反馈：下次课开头展示 2 份 `.dockerignore`，点评"漏排 `.env`"和"把 `venv` 打进镜像"两个高频问题。

## 十、无 AI 环境下的调整

- 本课次**不依赖 AI**：Dockerfile 由教师提供模板，学生照抄后逐行理解。
- 离线环境提前准备基础镜像与依赖；pip 源不可用时改用本地 wheel 缓存。
- 若环境允许，可让学生用 AI 解释构建日志，但要求自己复现一次失败并修复。

## 十一、对应教材与资源

- 教材：第18章 18.3–18.4（Dockerfile 指令、镜像构建与优化）。
- 项目：`duty/Dockerfile`、`duty/.dockerignore`、`duty_frontend/Dockerfile`、`duty_frontend/.dockerignore`。
- 代码：`duty/main.py`（`/health`、`0.0.0.0:8000`）、`duty_frontend/config.py`（`DUTY_API_BASE_URL`）。
- 下一课次：前后端服务部署——用环境变量和容器网络把两个容器连起来。
