#!/usr/bin/env/python
# File name   : server.py
# Production  : GWR
# Website     : www.adeept.com
# Author      : William
# Date        : 2020/03/17

import time
import threading
import os
import asyncio
import websockets
import socket
import json

import system_info
import app


curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)


def function_select(command_input, response):
    global functionMode
    print(f"function_select command_input={command_input}")


def wifi_check():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.1.1.1", 80))
    ipaddr_check = s.getsockname()[0]
    s.close()
    print(ipaddr_check)


async def recv_msg(websocket, path):
    while True:
        response = {
            'status': 'ok',
            'title': '',
            'data': None
        }

        data = ''
        data = await websocket.recv()

        try:
            data = json.loads(data)
        except Exception as e:
            print('not A JSON')

        print(f"got websock message from {websocket}: {data}")

        if not data:
            continue

        if isinstance(data, str):
            print(f"recv_msg data={data}")

            function_select(data, response)

            if 'get_info' == data:
                response['title'] = 'get_info'
                response['data'] = [system_info.get_cpu_tempfunc(
                ), system_info.get_cpu_use(), system_info.get_ram_info()]

        else:
            pass

        print(data)
        response = json.dumps(response)
        await websocket.send(response)


if __name__ == '__main__':

    HOST = ''
    PORT = 10223  # Define port serial
    ADDR = (HOST, PORT)

    global flask_app
    flask_app = app.webapp()
    flask_app.startthread()

    while 1:
        wifi_check()
        try:  # Start server,waiting for client
            start_server = websockets.serve(recv_msg, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            # print('...connected from :', addr)
            break
        except Exception as e:
            print(e)

    try:
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
