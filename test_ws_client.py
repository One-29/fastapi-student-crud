"""
WebSocket 客户端测试脚本
测试 ws_demo.py 的并发推送和 echo 功能
"""
import asyncio
import websockets


async def run_concurrent_demo():
    uri = "ws://localhost:8000/ws"
    print(f"连接到 {uri}...")

    async with websockets.connect(uri) as ws:
        print("✓ 连接成功\n")

        # 1. 接收 3 次定时推送
        print("--- 测试定时推送 ---")
        for i in range(3):
            msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
            print(f"  收到: {msg}")

        # 2. 发送消息测试 echo（此时定时推送仍在并发运行）
        print("\n--- 测试 echo（定时推送仍在后台） ---")
        await ws.send("Hello WebSocket")
        echo_msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
        print(f"  发送: Hello WebSocket")
        print(f"  回显: {echo_msg}")

        # 3. 再收一次定时推送，证明 echo 没有阻塞定时
        print("\n--- 验证并发（echo 后定时推送仍工作） ---")
        time_msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
        print(f"  收到: {time_msg}")

        print("\n✓ 并发测试通过：定时推送和 echo 同时工作")
        print("关闭连接...")


if __name__ == "__main__":
    try:
        asyncio.run(run_concurrent_demo())
        print("\n✓ 测试完成，无异常")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
