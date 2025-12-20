# 智慧树问答工具

```txt
   ╱|、　　　　　　　　　　　ฅ^•ﻌ•^ฅ
  (˚ˎ 。7　　　　　　　　 喵喵感谢~
   |、˜〵　　　　　　　　　 求星星啦~⭐
   じしˍ,)ノ
```

## 环境安装

Python >= 3.10

```bash
# 升级 pip 并配置国内镜像源
python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 安装依赖
pip install -r requirements.txt

# 或使用 uv（推荐）
# 安装 uv: https://docs.astral.sh/uv/getting-started/installation/
uv sync
uv run python ./main.py
```

## 配置指南

### 📁 配置文件结构

项目使用 TOML 格式配置文件（`config.toml`），支持环境变量注入。

```toml
# config.toml
[account]
username = "${USERNAME}"  # 支持环境变量或 .env 文件
password = "${PASSWORD}"

[option]
driver = "msedge"
browser_path = ""
delay_time_s = 10
enabled_random_time = true
Q_A_urls = [
    "https://qah5.zhihuishu.com/qa.html#/web/home/...",
    "https://other-course-url..."
]

[llm]
base_url = "https://api.deepseek.com/v1"
api_key = "${OPENAI_API_KEY}"
model = "deepseek-chat"
max_tokens = 500
temperature = 1.3

[log]
level = "DEBUG"
file_level = "WARNING"
file_path = "log/app.log"
colorful_output = true
rotation = "10 MB"
retention = 5
time_format = "%Y-%m-%d %H:%M:%S"
```

### 🛠️ 核心配置详解

1. **账户认证模块**

   ```toml
   [account]
   # 登录账号和密码，支持环境变量注入
   username = "${USERNAME}"  # 环境变量 USERNAME 的值
   password = "${PASSWORD}"  # 环境变量 PASSWORD 的值
   ```

   - 不填写用户名密码也可以通过扫码登录
   - 推荐使用环境变量或 `.env` 文件存储敏感信息

2. **浏览器控制模块**

   ```toml
   [option]
   # 浏览器驱动类型（支持多种浏览器）
   # 可选值: chrome、msedge、chrome-beta、msedge-beta、chrome-dev、msedge-dev、chrome-canary、msedge-canary
   driver = "msedge"

   # 浏览器执行路径（留空则自动发现）
   # Windows 示例: "C:/Program Files/Google/Chrome/Application/chrome.exe"
   # macOS 示例: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   browser_path = ""

   # 延迟设置策略
   delay_time_s = 10                # 操作延迟基准（秒），推荐 8-15 秒
   enabled_random_time = true       # 是否启用随机延时（±50% 偏移）

   # 问答页面 URL 列表
   Q_A_urls = [
       "https://qah5.zhihuishu.com/qa.html#/web/home/1000010387?role=2&recruitId=360873&VNK=5a97a88c",
       "https://qah5.zhihuishu.com/qa.html#/web/home/1000087124?role=2&recruitId=336325&VNK=ae7462aa"
   ]
   ```

3. **AI 模型设置**

   ```toml
   [llm]
   # API 地址
   base_url = "https://api.deepseek.com/v1"

   # API 密钥（推荐使用环境变量）
   api_key = "${OPENAI_API_KEY}"    # 环境变量 OPENAI_API_KEY 的值

   # 模型选择
   model = "deepseek-chat"

   # 生成参数控制
   max_tokens = 500                 # 最大生成 token 数（200-1500）
   temperature = 1.3                # 采样温度，控制输出随机性（0.0-2.0）
   ```

4. **日志配置**

   ```toml
   [log]
   # 控制台日志级别（从高到低）：
   # CRITICAL > ERROR > WARNING > INFO > DEBUG > TRACE
   level = "DEBUG"

   # 文件日志级别（独立控制）
   file_level = "WARNING"           # 例如：控制台看 DEBUG，文件只存 WARNING 及以上

   # 日志文件路径
   file_path = "log/app.log"

   # 输出格式
   colorful_output = true           # 是否启用彩色日志输出

   # 日志轮转配置
   rotation = "10 MB"              # 单个日志文件最大大小
   retention = 5                   # 保留历史日志文件数量

   # 时间戳格式
   time_format = "%Y-%m-%d %H:%M:%S"
   ```

### ▶️ 运行

```bash
# 直接运行
python ./main.py

# 或使用 uv（推荐）
uv run python ./main.py
```

### 🛡️ 环境变量配置

推荐使用 `.env` 文件管理敏感信息：

```bash
# .env
USERNAME=your_zhihuishu_username
PASSWORD=your_zhihuishu_password
OPENAI_API_KEY=your_openai_api_key
```

确保 `.env` 文件已添加到 `.gitignore` 中，避免泄露敏感信息。
