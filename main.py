from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger
from typing import List

class ConnectionManger:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broastcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

class Comment:
    def __init__(self, author, content):
        self.author = author
        self.content = content

app = FastAPI()
templates = Jinja2Templates("templates")
manager = ConnectionManger()
comments = []
comments.append(Comment("author 1", "content 1"))
comments.append(Comment("author 2", "content 2"))
comments.append(Comment("author 3", "content 3"))

@app.get('/client')
async def client(request: Request):
    return templates.TemplateResponse("client.html", {"request": request, "comment":comments})

# 웹소켓 설정
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(f'client connected : {websocket.client}')
    await manager.connect(websocket)
    # await websocket.accept() # 클라이언트의 websocket 접속 허용
    # await websocket.send_text(f"Welcome : {websocket.client}")

    try:
        while True:
            data = await websocket.receive_json() # 메시지 수신 대기
            comments.append(Comment(data['author'], data['content']))
            print(f'message received : {data} from {websocket.client}')
            # await websocket.send_text(f"Message text was: {data}") # 클라이언트에 전달
            await manager.broastcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 개발, 디버깅용 구동 함수
def run():
    import uvicorn
    uvicorn.run(app)

# python main.py 로 할 경우 실행되는 구문
if __name__ == '__main__':
    run()