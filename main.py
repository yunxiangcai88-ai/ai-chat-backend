import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

# -------- 日志配置，方便调试 --------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------- 读取并清洗 OPENAI_API_KEY --------
raw_key = os.environ.get("OPENAI_API_KEY", "")

# 打印 repr，确认到底有没有奇怪字符（只在启动时打一次）
logger.info("RAW OPENAI_API_KEY repr: %r", raw_key)

# 去掉前后空白 + 所有换行符，防止 header 里非法字符
OPENAI_API_KEY = raw_key.strip().replace("\n", "").replace("\r", "")

if not OPENAI_API_KEY:
    raise RuntimeError("请先在环境变量中设置 OPENAI_API_KEY（或它是空的）")

if OPENAI_API_KEY != raw_key:
    logger.warning("OPENAI_API_KEY 中包含空白/换行，已在代码中自动清理。")

# -------- 创建 OpenAI 客户端 --------
client = OpenAI(api_key=OPENAI_API_KEY)

# -------- FastAPI 初始化 --------
app = FastAPI(title="Simple Chat Backend")

# 允许的前端来源（开发阶段可以用 "*"，上线后建议改成你自己的域名）
allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "*",  # 调试阶段先放开
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
            model="gpt-5.1",  # 或你想用的其他模型
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_msg},
            ],
        )
        reply_text = completion.choices[0].message.content
        return ChatResponse(reply=reply_text)
    except Exception as e:
        # 防止异常直接 500 黑盒，看不见原因
        logger.exception("调用 OpenAI 出错: %s", e)
        return ChatResponse(reply=f"[后端调用 OpenAI 出错]: {e}")
