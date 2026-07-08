import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI()

# 全局：所有活跃的 WebSocket 连接
active_connections: list[WebSocket] = []

# 一个内嵌的极简网页客户端，方便用浏览器测 WebSocket 多人广播
PAGE = """
<!doctype html>
<html>
  <body>
    <h3>WebSocket 多人广播 demo</h3>
    <p>提示: 输入 <b>开始</b> 建立连接，输入 <b>返回</b> 结束通话</p>
    <p style="color: blue;">💡 多开几个标签页测试广播效果！</p>
    <input id="msg" placeholder="输入内容" />
    <button onclick="send()">发送</button>
    <ul id="log"></ul>
    <script>
      let ws = null;

      function send() {
        const box = document.getElementById("msg");
        const text = box.value.trim();
        box.value = "";

        if (text == "开始") {
          if (ws && ws.readyState === WebSocket.OPEN) {
            const li = document.createElement("li");
            li.textContent = "已经连接了";
            li.style.color = "orange";
            document.getElementById("log").appendChild(li);
            return;
          }
          ws = new WebSocket("ws://localhost:8000/ws");
          ws.onopen = () => {
            const li = document.createElement("li");
            li.textContent = "✓ 连接已建立";
            li.style.color = "green";
            document.getElementById("log").appendChild(li);
          };
          ws.onmessage = (e) => {
            const li = document.createElement("li");
            li.textContent = e.data;
            document.getElementById("log").appendChild(li);
          };
          ws.onclose = () => {
            const li = document.createElement("li");
            li.textContent = "✗ 连接已断开";
            li.style.color = "gray";
            document.getElementById("log").appendChild(li);
          };
        }
        else if (text == "返回") {
          const li = document.createElement("li");
          li.textContent = "下次再见";
          li.style.color = "red";
          document.getElementById("log").appendChild(li);
          if (ws) ws.close();
          ws = null;
        }
        else {
          if (!ws || ws.readyState !== WebSocket.OPEN) {
            const li = document.createElement("li");
            li.textContent = "请先输入开始建立连接";
            li.style.color = "orange";
            document.getElementById("log").appendChild(li);
            return;
          }
          ws.send(text);
        }
      }
    </script>
  </body>
</html>
"""


@app.get("/")
async def index():
    return HTMLResponse(PAGE)


async def broadcast(message: str):
    """广播消息给所有在线连接"""
    for conn in active_connections:
        try:
            await conn.send_text(message)
        except Exception as e:
            print(f"广播失败: {e}")


@app.websocket("/ws")
async def ws_chat(websocket: WebSocket):
    # 1. 握手 + 加入房间
    await websocket.accept()
    active_connections.append(websocket)

    # 广播：新人进入
    await broadcast(f"📢 新用户加入！当前在线: {len(active_connections)} 人")
    print(f"✓ 新连接加入，当前在线: {len(active_connections)}")

    try:
        # 2. 持续监听这个连接的消息
        while True:
            text = await websocket.receive_text()

            # 3. 收到消息后，广播给所有人（包括发送者自己）
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] {text}"
            await broadcast(message)

    except WebSocketDisconnect:
        # 4. 断开时从列表移除
        active_connections.remove(websocket)
        print(f"✗ 连接断开，剩余在线: {len(active_connections)}")

        # 广播：有人离开
        await broadcast(f"📢 有用户离开，当前在线: {len(active_connections)} 人")