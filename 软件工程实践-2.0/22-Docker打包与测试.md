# 第 22 章 Docker 打包与测试

上一章讲了为什么打包、打成什么，以及怎样用 Dockerfile 描述一个镜像。但描述只有交给构建命令执行，才会变成真正可运行的镜像；镜像能否运行、构建是否高效，也只有在执行之后才看得出来。

这一步走通之后，构建的快慢与产物的体积才开始成为可以比较的问题。前后端联通留到下一章。

> 环境提示：本章的 `docker build`、`docker run` 需要 Docker 守护进程运行。教材编写环境的 Docker Desktop 未启动，因此本章的命令与预期结果未实际构建验证，只按项目文件核对了命令语义与 Dockerfile 内容。读者执行前先确认 `docker info` 可用。

## 本章要解决的问题

**怎样把 Dockerfile 变成能运行的镜像，并让构建更快、镜像更小？**

Dockerfile 写好了，第一次构建该执行什么命令？构建出来的镜像又该怎样运行、怎样验证？这些问题没有回答，就谈不上优化。

代码没有变复杂，交付却一次比一次慢，产物一次比一次大。没有人改错，只是每个看起来无害的先后顺序都在悄悄累积代价；等到察觉时，已经说不清是从哪一步开始的。

本章关心的是：构建出来的东西凭什么能运行，以及构建的快慢与产物的体积，究竟由哪些先后顺序决定。

## 本章学习目标

读完第 22 章并完成实训后，你应该能：

1. 构建、运行并验证后端镜像，能读取容器日志定位启动失败。
2. 说明构建上下文与 `.dockerignore` 对镜像体积和构建速度的影响。
3. 按“先依赖、后代码”的顺序写后端 Dockerfile，并指出缓存失效的常见写法。
4. 为 Streamlit 前端写 Dockerfile，正确设置启动参数。
5. 识别“容器里的 `127.0.0.1`”问题，并做基础镜像体积优化。

## 22.1 从 Dockerfile 到镜像：第一次构建

第 21 章已经把后端运行所需的内容写进了 Dockerfile，本章直接拿它做第一次构建：

**代码 22-1-1** · `duty/Dockerfile`（后端镜像，Python）

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

文件最后一行 `CMD ["python", "main.py"]` 是后端的启动配置：容器创建后执行这条命令，FastAPI 才会监听 8000。前端也需要启动配置，只是 Streamlit 的服务参数更多，放到 22.4 对照。

**docker build 做的三件事**

`docker build` 做三件事：读取 Dockerfile、把构建上下文（命令末尾 `.` 指向的目录）发给 Docker 守护进程、按指令逐层生成镜像。第一次构建没有缓存可用，耗时最长，这是正常的。进入后端目录执行：

**代码 22-1-2** · 命令（Bash）

```bash
cd duty
docker build -t duty-backend:1.0 .
docker images | grep duty-backend
```

`-t` 给镜像起名并打标签，格式为 `名称:标签`；不写标签时默认 `latest`。`docker build` 的常用参数如下（本章的构建命令只用到 `-t`，其余按需使用）：

| 参数 | 作用 |
| --- | --- |
| `-t 名称:标签` | 给镜像命名并打版本标签 |
| `-f Dockerfile 路径` | 指定 Dockerfile；默认使用上下文根目录的 `Dockerfile` |
| `--no-cache` | 本次构建不复用缓存，用于确认问题是否由缓存引起 |
| `--pull` | 构建前重新拉取基础镜像，避免一直使用本机旧版本 |
| `--build-arg 键=值` | 传入构建期变量，对应 Dockerfile 中 `ARG` 声明的值 |
| `--target 阶段名` | 只构建多阶段中的某一阶段，多阶段构建时使用 |

`docker build --help` 可以查看完整参数；命令末尾的 `.` 不能漏，它决定 `COPY` 从哪里找文件，下一节展开。

构建日志（Build Log）把每条 `RUN` / `COPY` 显示为一步：第一次构建每一步都会执行；不改任何文件再构建一次，会看到对应步骤显示 `CACHED`，说明这一层被复用。最后没有报错，并且 `docker images` 能看到新镜像，构建就完成了。

**用 docker run 启动并验证**

镜像构建出来后，用 `docker run` 启动容器：

**代码 22-1-3** · 命令（Bash）

```bash
docker run -d --name duty-backend -p 8000:8000 duty-backend:1.0
docker ps
curl http://127.0.0.1:8000/health
```

预期返回 `{"status":"healthy"}`。再看三处：浏览器打开 `http://127.0.0.1:8000/docs`；`docker logs duty-backend` 看启动日志；`docker exec -it duty-backend sh` 进入容器查看 `/app`。

`docker run` 的常用参数如下（前三个本章的代码会用到，`--rm` 适合调试，最后三个在下一章部署时会用到）：

| 参数 | 作用 |
| --- | --- |
| `-d` | 后台运行，终端不被容器占用 |
| `--name 名称` | 给容器起名，方便 `logs` / `exec` / `rm` |
| `-p 宿主机端口:容器端口` | 端口映射，例如 `-p 8000:8000` |
| `--rm` | 容器停止后自动删除，适合一次性调试 |
| `-e 键=值` | 注入环境变量 |
| `-v 宿主机路径:容器路径` | 挂载目录或卷，数据不随容器删除而丢失 |
| `--network 网络名` | 指定容器网络，让容器之间按名字互访 |

`docker logs` 也有常用参数：默认输出全部日志，`-f` 持续跟踪新日志，`--tail 50` 只看最后 50 行。排查启动失败时，先看最后几十行。

到这里，第一次构建、运行与验证完成。接下来解释两件常被忽略的事：为什么构建上下文会让构建变慢，以及为什么层顺序会让缓存失效。

## 22.2 构建上下文与忽略规则

22.1 的 `docker build ... .` 里，末尾的 `.` 不是 Dockerfile 所在目录，而是**构建上下文**（Build Context）：Docker 把这个目录整体发给守护进程，`COPY` 的源路径都相对于它。因此构建命令要在项目根目录执行；`COPY requirements.txt .` 找的是上下文根部的 `requirements.txt`。上下文越大，发送与扫描越慢，无关文件也越容易被复制进镜像；`.dockerignore` 就是给上下文做减法。

**.dockerignore 与三项底线**

一个可用的 `.dockerignore` 起点是下面这份清单：

**代码 22-1-4** · 示例（文本）

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
```

三项底线：`.env` 不能进镜像（含密钥）；`venv/` 不能进镜像（本机虚拟环境）；`*.sqlite3` 与 `*.log` 不能进镜像（本机数据与日志）。再加 `.git/`、`__pycache__/`，上下文会小很多。

**两份 .dockerignore**

本章会构建两个镜像，因此有两个构建上下文：`duty/` 与 `duty_frontend/`；`.dockerignore` 要分别放在这两个目录的根部，内容可以相同，在 `duty_frontend/` 里构建时，`duty/` 的忽略规则不会自动生效。

忽略规则写得太宽，可能把运行需要的静态文件、模板、配置示例也排除掉，构建成功但运行报“文件不存在”；写得太松，`venv/`、日志、数据库又进了镜像。一个可用的判据是：**构建后用 `docker run ... ls` 看一遍 `/app`，确认“运行需要的都在、运行不需要的都不在”。**

构建与运行中最常见的问题可以先查下表：

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

> 💡 **易错点**：以为 `.dockerignore` 会删除已经进入镜像的文件。它只影响“下一次构建时上下文里有什么”；已经构建出的镜像要重新构建才会变小。

## 22.3 缓存与层顺序

构建上下文决定一次构建要处理多少文件，层顺序决定第二次构建能复用多少。上下文已经通过 `.dockerignore` 控制住，这一节看层顺序。

**先 COPY . . 的代价**

一个典型的错误写法是：先 `COPY . .`，再 `RUN pip install -r requirements.txt`。它会把整个项目（包括 `venv/`、`.git/`、日志、数据库）先复制进镜像，再装依赖。后果有两个：

| 后果 | 原因 |
| --- | --- |
| 镜像大 | `venv/`、`.git/`、日志、数据库全进了镜像层 |
| 缓存失效 | 任何文件变化都会让 `COPY . .` 这一层变化，后面的 `RUN pip install` 全部重建 |

**缓存**是 Docker 按层复用的机制（Docker 官方文档）：某一层变了，它和它上面的所有层都要重建；下面的层命中缓存。构建顺序的核心原则可以概括为一句话：“把变化频繁的内容放在后面”。

> 💡 **易错点**：把 `COPY . .` 放在装依赖之前。业务代码一改，依赖层就失效，每次构建都重新装库；正确写法是先复制依赖清单、装依赖，再复制代码。

**Dockerfile 的六行顺序**

回到 22.1 的代码 22-1-1，逐行看它为什么这样排：

| 顺序 | 指令 | 为什么放这里 |
| --- | --- | --- |
| 1 | `FROM` | 基础环境固定 |
| 2 | `WORKDIR` | 后续路径都在 `/app` |
| 3 | `COPY requirements.txt .` | 依赖清单变化少，先复制 |
| 4 | `RUN pip install` | 依赖层尽量复用 |
| 5 | `COPY . .` | 代码变化频繁，放最后 |
| 6 | `ENV` | 运行行为固定 |
| 7 | `EXPOSE` / `CMD` | 声明端口与启动方式 |

改一行业务代码后再执行 `docker build -t duty-backend:1.1 .`，构建日志里 `COPY requirements.txt .` 与 `RUN pip install` 显示 `CACHED`，只有 `COPY . .` 及其后的层重新执行，依赖层命中缓存。反过来，如果改了 `requirements.txt`，依赖层及其上层都会重建，基础层仍然命中缓存。

## 22.4 前端镜像的启动参数

本章说的**前端**，指第 20 章完成的 Streamlit 应用（`duty_frontend/`）：它用 Python 写页面，自带 Web 服务，不是用 Node/React 构建出的静态站点。因此它的 Dockerfile 与后端结构相似。后端的启动配置已经在 22.1 给出（`CMD ["python", "main.py"]`）；前端同样在容器启动时执行一条命令，区别在 Streamlit 需要显式指定端口、监听地址与 headless 模式。

**代码 22-1-5** · `duty_frontend/Dockerfile`（前端镜像，Python）

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

**Streamlit 的三个启动参数**

Streamlit 的启动参数写在 `CMD` 里，三个参数各管一件事：

| 参数 | 作用 | 不写会怎样 |
| --- | --- | --- |
| `--server.port=8501` | 指定端口 | 默认 8501，但写出来更明确 |
| `--server.address=0.0.0.0` | 监听所有网卡 | 只监听容器内回环，宿主机访问不到 |
| `--server.headless=true` | 不自动打开浏览器 | 容器里会尝试开浏览器，报错或卡住 |

写好 Dockerfile 后，进入前端目录构建并启动：

**代码 22-1-6** · 命令（Bash）

```bash
cd duty_frontend
docker build -t duty-frontend:1.0 .
docker run -d --name duty-frontend -p 8501:8501 duty-frontend:1.0
```

浏览器打开 `http://127.0.0.1:8501`，页面能加载。但只要页面请求后端数据（例如登录），请求就会失败——这正是下面要解释的问题。

> 💡 **易错点**：只写 `EXPOSE 8501` 就以为宿主机能访问。`EXPOSE` 是声明，`-p 8501:8501` 才是端口映射；前端还要监听 `0.0.0.0`，否则只在容器内可见。

**容器里的 127.0.0.1**

登录失败的原因在 `duty_frontend/config.py`：

**代码 22-1-7** · 示例代码（Python）

```python
API_BASE_URL = os.getenv("DUTY_API_BASE_URL", "http://127.0.0.1:8000")
```

这行代码在容器里执行时，`127.0.0.1` 指的是前端容器自己，不是宿主机，也不是后端容器。前端在找“自己身上的 8000 端口”，当然连不上。

本章只记录现象与原因，不解决；下一章用环境变量 `DUTY_API_BASE_URL` 与容器网络让前端找到后端。

## 22.5 镜像体积优化与多阶段构建

**体积来自哪一层**

优化之前先看体积来自哪里：

**代码 22-1-8** · 命令（Bash）

```bash
docker images
docker history duty-backend:1.0
```

`docker images` 看总量，`docker history` 按层列出每一层的大小。先找出占比最大的层，再决定优化哪一项。

**五项优化的顺序**

优化按从易到难排序（Docker 官方文档与 OWASP Docker Security 的建议，按课程项目排序）；前四项只改 Dockerfile 的一两行，最后一项要调整文件结构：

1. 换用精简基础镜像（`slim`），去掉编译工具与文档。
2. 先复制依赖清单并安装依赖，再复制代码，让依赖层长期命中缓存。
3. 安装依赖时加 `--no-cache-dir`，不把 pip 下载缓存留在镜像里。
4. 用 `.dockerignore` 排除虚拟环境、日志、数据库等无关文件。
5. 采用多阶段构建：构建阶段安装工具、生成产物，运行阶段只复制产物。

每做一项就重新构建并比对体积，确认没有影响运行；不要一次改五处，否则体积没降下来时不知道是哪一项无效。

最后一项多阶段构建的写法是：第一个 `FROM` 作为构建阶段，装编译工具、构建产物；第二个 `FROM` 用精简基础镜像，只 `COPY --from=构建阶段` 需要的产物（Docker 官方文档）。这样运行镜像里没有构建工具，体积更小、攻击面更窄。

先能跑，再优化。不要为了省几十 MB 删掉运行必需的文件，也不要为了“看起来小”把日志、数据库打进镜像。

为了减小体积删掉调试工具、系统库，镜像小了，但出问题时无法进容器排查；保留工具，排查方便，但镜像大、攻击面宽。一个折中的做法是：运行镜像保持精简，需要排查时用同版本的调试镜像或临时安装工具；不要把“排错便利”永久写进生产镜像。

> 💡 **易错点**：为了减小体积删掉运行必需的依赖或系统库。镜像能构建、容器能启动，但某个接口一调用就报缺库；优化后必须重新跑 `/health` 与核心接口，确认功能未受影响。

## 示范例题

#### 例 22-1：为后端写 Dockerfile

**题目**：为 FastAPI 后端写一个 Dockerfile：使用 `python:3.12.9-slim`，工作目录 `/app`，安装 `requirements.txt`，复制代码，暴露 8000，启动 `python main.py`。说明为什么先复制依赖文件。

**解**：

**代码 22-2-1** · Dockerfile 片段

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
```

先复制 `requirements.txt` 并安装依赖，是为了让依赖层在业务代码变化时仍命中缓存；`COPY . .` 放在最后，改代码只重建代码层。`--no-cache-dir` 避免把 pip 缓存打进镜像。

#### 例 22-2：诊断镜像体积

**题目**：`docker history` 显示某镜像各层大小为：基础层 130 MB、依赖层 220 MB、代码层 15 MB、其他 5 MB。请指出体积主要来自哪里，并给出三条可行的优化建议。

**解**：

1. 体积主要来自依赖层（220 MB）与基础层（130 MB）。
2. 优化建议：换更精简的基础镜像（如 `slim`，已经使用则检查是否引入了编译工具）；安装依赖时加 `--no-cache-dir`，避免缓存层；把只在构建阶段需要的工具放到多阶段构建的构建阶段，运行阶段只拷产物；用 `.dockerignore` 排除虚拟环境、日志、数据库等无关文件。
3. 注意：不要为了减小体积删掉运行必需的系统库或依赖；优化后要重新运行 `/health` 与核心接口，确认功能未受影响。

## 独立习题

#### 习题 22-1

**题目**：某同学改了业务代码后重新构建，发现依赖层也重建了。请分析可能原因，并给出修正方法。

#### 习题 22-2

**题目**：有人主张“镜像越小越好”，为此删除了容器内的调试工具与部分系统库；也有人主张“能跑优先，体积其次”。请评价两种做法，并给出你的优化原则。

## ◆ 实训 22-1：Docker 打包与测试

### 一、任务目标与验收

| 目标 | 验收标志 |
| --- | --- |
| 后端镜像可构建 | `docker build` 成功，镜像可运行 |
| 缓存有效 | 只改代码时依赖层不重建 |
| 运行验证 | 容器内服务可访问、日志正常 |
| 前端镜像可启动 | 页面可访问，能说明后端地址为何仍不通 |
| 体积有优化 | 能说明至少两项优化 |

### 二、课前准备

- Docker 已安装并可运行
- 第 20 章的前后端代码
- 一份 `.dockerignore` 草稿

### 三、操作步骤

1. **构建并运行后端镜像**
   - 做什么：用 22.1 的 Dockerfile 完成第一次构建与启动
   - 操作：`docker build -t duty-backend:1.0 .`，再 `docker run -d --name duty-backend -p 8000:8000 duty-backend:1.0`
   - 预期输出：`docker ps` 能看到容器，`curl http://127.0.0.1:8000/health` 返回 `{"status":"healthy"}`
   - 做错会看到什么：容器退出 → `docker logs duty-backend` 看最后几行；端口被占用 → 改用 `-p 8001:8000`
2. **控制构建上下文**
   - 做什么：用 `.dockerignore` 缩小上下文，并比较构建速度
   - 操作：按 22.2 写入忽略项，重新构建，对比构建耗时与镜像体积
   - 预期输出：上下文明显变小，`venv/`、`.env` 不在镜像里
   - 做错会看到什么：`.env` 仍进镜像 → 检查忽略规则路径，并确认是重新构建而不是查看旧镜像
3. **验证缓存顺序**
   - 做什么：改一行业务代码，再构建一次，观察哪些层重建
   - 操作：执行 `docker build -t duty-backend:1.1 .`，看构建日志
   - 预期输出：`COPY requirements.txt` 与 `RUN pip install` 显示 `CACHED`，只有代码层及其后重建
   - 做错会看到什么：依赖层也重建 → `COPY . .` 放在了装依赖之前
4. **打包并运行前端**
   - 做什么：为 Streamlit 前端写 Dockerfile，构建并启动
   - 操作：按 22.4 写文件，`docker build -t duty-frontend:1.0 .`，再 `docker run -d --name duty-frontend -p 8501:8501 duty-frontend:1.0`
   - 预期输出：浏览器能打开 `http://127.0.0.1:8501`；记录数据请求的报错
   - 做错会看到什么：页面打不开 → 检查 `--server.address=0.0.0.0` 与端口映射；登录失败 → 记录容器内的 `127.0.0.1` 问题，下一章解决
5. **优化体积**
   - 做什么：比较基础镜像、缓存与多阶段构建对体积的影响
   - 操作：换 `slim` 基础镜像、加 `--no-cache-dir`、清理无关文件；有余力时试多阶段构建
   - 预期输出：体积下降，`/health` 与核心接口仍正常
   - 做错会看到什么：为省体积删掉运行依赖 → 回归验证，补回依赖

### 四、排错清单

| 现象 | 先查什么 |
| --- | --- |
| 构建很慢 | 构建上下文过大或缓存顺序错 |
| 容器启动即退出 | 启动命令错误、端口不匹配 |
| 前端请求失败 | 容器内地址、跨域、网络 |
| 镜像过大 | 基础镜像、缓存文件、无用依赖 |

### 五、提交与验收

提交两个 Dockerfile、构建与运行记录、体积对比；验收按“可构建运行”“缓存与优化”“前端打包”三项判定。

### 六、课后扩展

- 用多阶段构建减小前端镜像
- 给镜像打版本标签
- 写一份构建失败排查清单
- **复习任务**：回看第 21 章 21.3–21.4（分层与缓存）与第 5 章 5.4（依赖清单），对照本章 22.2–22.3，说明哪一层变化会让依赖层失效、为什么

## 本章小结

**核心结论**：

1. `docker build` 读取 Dockerfile，把构建上下文（命令末尾 `.` 所指的目录）发给守护进程，逐层生成镜像；`COPY` 的源路径相对于上下文，常用参数有 `-t`、`-f`、`--no-cache`、`--pull`、`--build-arg`、`--target`。
2. `.dockerignore` 给构建上下文做减法，守住 `.env`、虚拟环境、数据库与日志三条底线。
3. 缓存按层复用；正确顺序是先依赖后代码，改代码只重建代码层，改 `requirements.txt` 才重建依赖层。
4. 运行用 `-d --name -p`（以及 `-e` / `-v` / `--network`）；验证用 `/health`、`/docs`、`docker logs`、`docker exec`；容器里的 `127.0.0.1` 指容器自己。
5. 体积优化按“slim → 先依赖后代码 → `--no-cache-dir` → `.dockerignore` → 多阶段构建”的顺序；先能跑再优化，优化后必须回归。

把这章压缩成一句话：**先把 Dockerfile 构建成能跑的镜像，再让它更快更小：上下文与忽略规则决定体积，层顺序决定缓存。**

**学完本章，你可以体会到**：镜像构建的每个顺序都影响速度与可复现性，容器化是把“环境”也当成代码来管理。

**自检**：回到章首的学习目标，逐条问自己做到了没有——

- [ ] 构建、运行并验证后端镜像，能读取容器日志定位启动失败。
- [ ] 说明构建上下文与 `.dockerignore` 对镜像体积和构建速度的影响。
- [ ] 按“先依赖、后代码”的顺序写后端 Dockerfile，并指出缓存失效的常见写法。
- [ ] 为 Streamlit 前端写 Dockerfile，正确设置启动参数。
- [ ] 识别“容器里的 `127.0.0.1`”问题，并做基础镜像体积优化。

**下一章预告**：两个容器各自能跑，但前端还找不到后端。下一章用环境变量与 compose 把前后端连起来，完成整套部署。
