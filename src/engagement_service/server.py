#!/usr/bin/env python3
"""
 This was originally pilfered from
 https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/app.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"Great artists steal". Thank you, @adeept and @miguelgrinberg!
"""

import os
import sys
import threading
import psutil
import json
import logging

from flask import Flask, Response, send_from_directory
from flask_cors import CORS

from common.setup_logging import setup_logging
from engagement_service.engagement import Engagement
from engagement_service.head import Head


app = Flask(__name__)
CORS(app, supports_credentials=True)

head = Head()
# this starts a thread that engages with the huuuumans
engagement = Engagement(head)

dir_path = os.path.dirname(os.path.realpath(__file__))


def json_response(data):
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/stats')
def send_stats():
    return json_response({
        "engagement": Engagement.stats(),
        "system": {
            "cpuPercent": psutil.cpu_percent(),
            "ram": psutil.virtual_memory()[2],
        },
    })


@app.route('/pauseEngagement')
def pause_engagement():
    Engagement.pause_engagement()
    return json_response({"status": "paused"})


@app.route('/resumeEngagement')
def resume_engagement():
    Engagement.resume_engagement()
    return json_response({"status": "resumed"})


@app.route('/centerHead')
def center_head():
    head.center_head()


@app.route('/<path:filename>')
def sendgen(filename):
    return send_from_directory(dir_path, filename)


@app.route('/')
def index():
    return send_from_directory(dir_path, 'index.html')


class webapp:
    def thread(self):
        app.run(host='0.0.0.0', threaded=True)

    def startthread(self):
        # Define a thread for FPV and OpenCV
        fps_threading = threading.Thread(target=self.thread)
        # 'True' means it is a front thread,it would close when the mainloop() closes
        fps_threading.setDaemon(False)
        fps_threading.start()  # Thread starts


def start_app():
    setup_logging('engagement.log')
    logger = logging.getLogger(__name__)
    logger.info("app started")

    flask_app = webapp()
    flask_app.startthread()
