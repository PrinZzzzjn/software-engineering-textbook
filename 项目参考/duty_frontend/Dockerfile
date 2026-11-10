# 前端服务镜像（Streamlit）
# 与后端 Dockerfile 使用同一基础镜像与 pip 镜像，便于课堂统一演示
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12.9-slim

WORKDIR /app

# 配置 pip 国内镜像
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 先复制依赖文件，利用镜像层缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 再复制项目文件
COPY . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8501

# headless=true：容器内不自动打开浏览器；address=0.0.0.0：允许外部访问
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
