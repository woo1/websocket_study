import asyncio
import websockets

async def accept(websocket, path):
    while True:
        # 클라이언트 메시지 대기
        data = await websocket.recv()
        print("receive:", data, path)
        # 클라이언트로 전송
        await websocket.send(data)

start_server = websockets.serve(accept, "localhost", 9998)
# 비동기 서버 대기
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()