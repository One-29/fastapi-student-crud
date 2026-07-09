from fastapi.testclient import TestClient

from main import app


def test_chat_page_loads():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "实时聊天室" in response.text


def test_websocket_echoes_broadcast_message():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_text()
            websocket.send_text("hello")
            message = websocket.receive_text()

    assert "hello" in message
