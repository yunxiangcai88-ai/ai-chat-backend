import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from openai import OpenAI

# -------- 日志配置 --------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------- Jupyter 专用系统提示 --------
SYSTEM_PROMPT = """
You are an AI assistant used strictly as a backend for Jupyter Notebook.

Global rules (highest priority):
1. Always reply in **Markdown** format.

2. If the user question is a multiple-choice question
   (for example contains options like A/B/C/D, or (A)(B)(C)(D), or clearly asks to choose among options):
   - Reply **only** with the final choice (e.g., `C` or `C. 42`).
   - Do **not** provide any explanation or reasoning.
   - Do **not** output extra text, just the answer itself.

3. If the user asks for programming help / code, especially Python code for Jupyter Notebook:
   - Reply with **only one fenced code block**.
   - The code must be valid Python that can run directly in a Jupyter cell.
   - The code must contain **no comments** (no lines starting with `#`, no inline comments).
   - Do not output any extra explanation before or after the code block.

4. For all other questions (not clearly multiple-choice and not clearly about code),
   - Answer normally in Markdown (paragraphs, bullet points, headings allowed).
"""

# -------- 读取并清洗 API Key --------
raw_key = os.environ.get("OPENAI_API_KEY", "")
logger.info("RAW OPENAI_API_KEY repr: %r", raw_key)

OPENAI_API_KEY = raw_key.strip().replace("\n", "").replace("\r", "")

if not OPENAI_API_KEY:
    raise RuntimeError("请先在环境变量中设置 OPENAI_API_KEY（或它是空的）")

if OPENAI_API_KEY != raw_key:
    logger.warning("OPENAI_API_KEY 中包含空白/换行，已在代码中自动清理。")

client = OpenAI(api_key=OPENAI_API_KEY)

# -------- FastAPI 初始化 --------
app = FastAPI(title="Simple Chat Backend")

allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "*",  # 调试阶段先放开，之后可以换成你的前端域名
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
async def root():
    return {"status": "ok", "message": "Chat backend is running."}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    user_msg = req.prompt.strip()
    if not user_msg:
        return ChatResponse(reply="你什么都没说呀～")

    try:
        completion = client.chat.completions.create(
            model="gpt-5.1",  # 或其他模型
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        reply_text = completion.choices[0].message.content
        return ChatResponse(reply=reply_text)
    except Exception as e:
        logger.exception("调用 OpenAI 出错: %s", e)
        return ChatResponse(reply=f"[后端调用 OpenAI 出错]: {e}")

@app.get("/j_helper.py")
async def j_helper(request: Request):
    """
    返回一段 Python 源码，其中定义了 j(p: str) 函数。
    在 Jupyter 里 exec 这段代码后，就可以直接用 j("...") 提问。
    """
    base = str(request.base_url).rstrip("/")  # 例如 https://ai-chat-backend-0pr9.onrender.com

    code = """from urllib.request import Request, urlopen
from IPython.display import Markdown, display
import json

API_URL = "{api_url}"

def j(p: str):
    r = urlopen(
        Request(
            API_URL,
            json.dumps({{"prompt": p}}).encode(),
            {{"Content-Type": "application/json"}},
            method="POST",
        ),
        timeout=60,
    )
    display(Markdown(json.loads(r.read().decode()).get("reply", "")))
""".format(api_url=f"{base}/chat")

    return PlainTextResponse(code, media_type="text/x-python")
