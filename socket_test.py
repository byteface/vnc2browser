import websockets
import asyncio

# run the socket server
async def update(websocket, path):
    while True:
        # msg = await websocket.recv()
        await websocket.send("test")

server = websockets.serve(update, '0.0.0.0', 5555)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()


# just a test file to make sure ws works

# also setup the endpoint...
# https://www.nginx.com/blog/websocket-nginx/