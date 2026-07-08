import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from datetime import datetime
app = FastAPI()

# 一个内嵌的极简网页客户端，方便用浏览器测 WebSocket
PAGE = """
<!doctype html>
<html>
  <body>
    <h3>WebSocket echo demo</h3>
    <p>提示: 输入 <b>开始</b> 建立连接，输入 <b>返回</b> 结束通话</p>
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
            li.textContent = "连接已建立";
            li.style.color = "green";
            document.getElementById("log").appendChild(li);
          };
          ws.onmessage = (e) => {
            const li = document.createElement("li");
            li.textContent = "收到: " + e.data;
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


@app.websocket("/ws")
async def ws_echo(websocket: WebSocket):
    await websocket.accept()

    async def push_time():
        """每秒推送时间"""
        try:
            while True:
                await asyncio.sleep(1)
                now = datetime.now().strftime("%H:%M:%S")
                await websocket.send_text(f"当前时间: {now}")
        except  Exception as e:
            print(f"push_time 异常: {type(e).__name__}: {e}")

    async def echo():
        """接收消息并回显"""
        try:
            while True:
                text = await websocket.receive_text()
                await websocket.send_text(f"echo: {text}")
        except WebSocketDisconnect:
            print("client disconnected")

    # 并发运行两个任务
    await asyncio.gather(push_time(), echo())