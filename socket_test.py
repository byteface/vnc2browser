import websockets
import asyncio
import json

from domonic.events import *

# run the socket server
async def update(websocket, path):
    while True:
        msg = await websocket.recv()
        dom_event = json.loads(msg)
        print(msg)
        t = dom_event['type']

        if t == "keydown":
            evt = KeyboardEvent(t)
            evt.keyCode = dom_event['keyCode']
            print('keydown', evt)
      
        elif t == "keyup":
            evt = KeyboardEvent(t)
            evt.keyCode = dom_event['keyCode']
            print('keyup',evt)

        elif t == 'mousedown':
            evt = MouseEvent(t)
            evt.x = dom_event['clientX']
            evt.y = dom_event['clientY']
            # evt.buttons = dom_event['buttons']
            print('mousedown', evt)

        elif t == 'mouseup': 
            evt = MouseEvent(t)
            evt.x = dom_event['clientX']
            evt.y = dom_event['clientY']
            print('mouseup', evt)

        elif t == "mousemove":
            evt = MouseEvent(t)
            evt.x = dom_event['clientX']
            evt.y = dom_event['clientY']
            print('mousemove', evt)


        await websocket.send("test")

server = websockets.serve(update, '0.0.0.0', 5555)
asyncio.get_event_loop().run_until_complete(server)
asyncio.get_event_loop().run_forever()


# just a test file to make sure ws works

# also setup the endpoint...
# https://www.nginx.com/blog/websocket-nginx/
