from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["chat"])


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        disconnected: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except RuntimeError:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()

CHAT_PAGE = """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>实时聊天室</title>
    <style>
      body { font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; }
      #log { border: 1px solid #ddd; min-height: 300px; padding: 12px; list-style: none; }
      form { display: flex; gap: 8px; }
      input { flex: 1; padding: 8px; }
      button { padding: 8px 14px; }
    </style>
  </head>
  <body>
    <h1>实时聊天室</h1>
    <ul id="log"></ul>
    <form id="form">
      <input id="message" autocomplete="off" placeholder="输入消息" />
      <button>发送</button>
    </form>
    <script>
      const protocol = location.protocol === "https:" ? "wss" : "ws";
      const ws = new WebSocket(`${protocol}://${location.host}/ws`);
      const log = document.getElementById("log");
      const form = document.getElementById("form");
      const message = document.getElementById("message");

      ws.onmessage = (event) => {
        const item = document.createElement("li");
        item.textContent = event.data;
        log.appendChild(item);
      };

      form.addEventListener("submit", (event) => {
        event.preventDefault();
        const text = message.value.trim();
        if (!text) return;
        ws.send(text);
        message.value = "";
      });
    </script>
  </body>
</html>
"""


@router.get("/")
async def chat_index():
    return HTMLResponse(CHAT_PAGE)


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.broadcast(f"系统：新用户加入，当前在线 {len(manager.active_connections)} 人")

    try:
        while True:
            text = await websocket.receive_text()
            timestamp = datetime.now().strftime("%H:%M:%S")
            await manager.broadcast(f"[{timestamp}] {text}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"系统：有用户离开，当前在线 {len(manager.active_connections)} 人")
