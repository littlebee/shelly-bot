#!/usr/bin/env python3

import logging
import json
import asyncio
import websockets

import commons.paths as paths
import trainer

logging.basicConfig()

sockets = set()


def iseeu_message(websocket):
    remoteIp = websocket.remote_address[0]
    return json.dumps({
        "type": "iseeu",
        "data": {
            "ip": remoteIp,
        }
    })


async def send_message(websocket, message):
    if websocket and websocket != "all":
        await websocket.send(message)
    elif sockets:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([websocket.send(message) for websocket in sockets])


# NOTE that there is no "all" option here, need a websocket,
#  ye shall not ever broadcast this info
async def notify_iseeu(websocket):
    if not websocket or websocket == "all":
        return
    await send_message(websocket, iseeu_message(websocket))


async def register(websocket):
    print(f"got new connection from {websocket.remote_address[0]}")
    sockets.add(websocket)
    await notify_iseeu(websocket)


async def unregister(websocket):
    print(f"lost connection {websocket.remote_address[0]}")
    try:
        sockets.remove(websocket)
    except:
        pass


async def handleMessage(websocket, path):
    await register(websocket)
    try:
        async for message in websocket:
            print(message)
            jsonData = json.loads(message)
            messageType = jsonData.get("type")
            # messageData = jsonData.get('data')

            if messageType == "whoami":
                await notify_iseeu()
            elif messageType == "retrain":
                trainer.retrain_model()
            else:
                logging.error("received unsupported message: %s", jsonData)
    finally:
        await unregister(websocket)


print(f"Starting server on port {paths.TRAINER_SERVICE_PORT}")
start_server = websockets.serve(
    handleMessage, port=paths.TRAINER_SERVICE_PORT)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
