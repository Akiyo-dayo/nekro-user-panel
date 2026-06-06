FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 9054

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9054", "--log-level", "info"]
