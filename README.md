# Simple Chat Backend (FastAPI + OpenAI)

这个项目是给你前端 `index.html + main.js` 使用的后端接口示例，只提供一个接口：

- `POST /chat`  
  - 请求体：`{ "prompt": "用户输入" }`
  - 返回体：`{ "reply": "AI回复" }`

## 1. 本地运行步骤

1. 安装 Python 3.10+（建议 3.11）

2. 在项目目录下创建虚拟环境并激活：

   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # macOS / Linux
   # source .venv/bin/activate
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 设置环境变量 `OPENAI_API_KEY`（以 Windows PowerShell 为例）：

   ```powershell
   setx OPENAI_API_KEY "你的API密钥"
   ```

   macOS / Linux (bash)：

   ```bash
   export OPENAI_API_KEY="你的API密钥"
   ```

5. 启动服务（本地开发）：

   ```bash
   uvicorn main:app --reload --port 8000
   ```

   启动成功后：
   - 健康检查：`http://127.0.0.1:8000/`
   - 接口地址：`http://127.0.0.1:8000/chat`

6. 测试接口（示例 curl）：

   ```bash
   curl -X POST "http://127.0.0.1:8000/chat" ^
     -H "Content-Type: application/json" ^
     -d "{\"prompt\": \"你好，请用一句话介绍一下自己\"}"
   ```

## 2. 和前端对接

在你的前端 `main.js` 里，把 `API_URL` 改成部署后的 `/chat` 地址，例如：

```js
const API_URL = "https://your-service.onrender.com/chat";
```

本地调试时可以暂时写：

```js
const API_URL = "http://127.0.0.1:8000/chat";
```

## 3. 部署到 Render（示例）

这里给一个比较省心的付费路线：Render（PaaS 平台）。

1. 把这个项目放到一个 GitHub 仓库。
2. 打开 [Render](https://render.com) 注册账号并绑定 GitHub。
3. 点击 “New” → “Web Service”，选择你的仓库。
4. 配置：
   - Environment：`Python`
   - Build Command：`pip install -r requirements.txt`
   - Start Command：`uvicorn main:app --host 0.0.0.0 --port $PORT`
5. 在 “Environment” 里添加环境变量：
   - `OPENAI_API_KEY = 你的 OpenAI 密钥`
6. 选择实例类型：
   - 开始可以用免费或者 Starter 付费档（512MB 就够一个小接口用）。

部署完成后，Render 会给你一个类似：

```
https://your-service.onrender.com
```

的域名，你只要在前端把 `API_URL` 指向这个地址的 `/chat` 就可以了。

## 4. 注意事项

- 千万不要在前端 JS 或 HTML 里写明文的 API Key！
- 所有密钥都应该放在服务器的环境变量里。
- 如果你用的是 EdgeOne 或其他静态托管，前端是纯静态的，**只能调用这个后端接口**。
