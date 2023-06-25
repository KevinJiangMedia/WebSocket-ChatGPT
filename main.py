import time
# import logging
from fastapi import FastAPI, WebSocket, Response


app = FastAPI()
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger('WebSocket-ChatGPT')
# logger.setLevel(logging.INFO)
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)
# # add ch to logger
# logger.addHandler(ch)


@app.get("/")
async def index():
    # 读取html内容输出给客户端
    return Response(open("index.html", encoding="utf-8").read())


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


# 创建一个连接管理器
wsConnManager = ConnectionManager()


@app.websocket("/ws")
async def chat_websocket(websocket: WebSocket):
    # 与客户端建立连接
    await wsConnManager.connect(websocket)
    print("connected a websocket client")
    # logger.info("connected a websocket client")
    try:
        while True:
            # 接收客户端请求
            text = await websocket.receive_text()
            # logger.info("first message: %s", text)
            for i in range(12):
                time.sleep(1)
                # 向客户端发送数据
                await websocket.send_text(str(i))
                # 等待客户端确认并接收客户端回传数据
                text = await websocket.receive_text()
                # logger.info("in for text: %s", text)
                # 如果客户端发送了stop信号，则退出生成
                if text == 'stop':
                    # logger.info('接收到停止信号')
                    break
            # 向客户端发送生成完成的信号
            await websocket.send_text("_end_")
    except Exception:
        wsConnManager.disconnect(websocket)
