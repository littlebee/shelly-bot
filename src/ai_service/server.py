#!/usr/bin/env python3
"""
 This was originally pilfered from
 https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/app.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"Great artists steal". Thank you, @adeept and @miguelgrinberg!
"""

import os
import threading
import json
import psutil
import multiprocessing
import logging


from flask import Flask, Response, send_from_directory
from flask_cors import CORS

import cv2

from common.setup_logging import setup_logging
from ai_service.camera_opencv import Camera
from ai_service.base_camera import BaseCamera
from ai_service.face_detect import FaceDetect
from ai_service.trainer import Trainer
from ai_service.acquirer import Acquirer


app = Flask(__name__)
CORS(app, supports_credentials=True)

camera = Camera()
trainer = Trainer()
face_detect = FaceDetect(camera, trainer)
acquirer = Acquirer(camera)


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        # can't augment the frame directly from the camera as that will
        # alter it for all and you will see the face detection start to
        # stutter and blank out
        frame = frame.copy()
        # add names and bounding boxes
        frame = face_detect.augment_frame(frame)
        frame = acquirer.augment_frame(frame)
        jpeg = cv2.imencode('.jpg', frame)[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n')


def json_response(data):
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def respond_ok(data=None):
    return json_response({
        "status": "ok",
        "data": data
    })


def respond_not_ok(status, data):
    return json_response({
        "status": status,
        "data": data
    })


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/stats')
def send_stats():
    (a0_temp, cpu_temp, gpu_temp, *rest) = [
        int(i) / 1000 for i in
        os.popen(
            'cat /sys/devices/virtual/thermal/thermal_zone*/temp').read().split()
    ]
    return json_response({
        "capture": BaseCamera.stats(),
        "faceDetect": FaceDetect.stats(),
        "system": {
            "cpuPercent": psutil.cpu_percent(),
            "ram": psutil.virtual_memory()[2],
            "temp": {
                "A0": a0_temp,
                "CPU": cpu_temp,
                "GPU": gpu_temp
            }
        },
        "trainer": Trainer.stats()
    })


@app.route('/pauseFaceDetect')
def pause_face_detect():
    face_detect.pause()
    return respond_ok()


@app.route('/resumeFaceDetect')
def resume_face_detect():
    face_detect.resume()
    return respond_ok()


@app.route('/retrainModel')
def retrain_model():
    trainer.trigger_retrain()
    return respond_ok()


@app.route('/retrainAll')
def retrain_all():
    trainer.trigger_retrain_all()
    return respond_ok()


@app.route('/names')
def names():
    return respond_ok(acquirer.get_names())


@app.route('/nextFaces')
def next_faces():
    return respond_ok(face_detect.get_next_faces())


@app.route('/newFace')
def new_face():
    acquirer.new_face()
    return respond_ok()


@app.route('/acquireSpokenName')
def acquire_spoken_name():
    nameBin = acquirer.acquire_spoken_name()
    if not nameBin:
        return respond_not_ok('empty')

    return respond_ok(nameBin)


@app.route('/acquireImages')
def acquire_images():
    acquirer.acquire_images()
    return respond_ok()


@app.route('/saveNewFace')
def save_new_face():
    new_name = acquirer.save_new_face()
    trainer.trigger_retrain()
    return respond_ok(new_name)


@app.route('/ping')
def ping():
    return respond_ok('pong')


@app.route('/<path:filename>')
def send_file(filename):
    return send_from_directory(dir_path, filename)


@app.route('/')
def index():
    return send_from_directory(dir_path, 'index.html')


class webapp:
    def __init__(self):
        self.camera = camera

    def thread(self):
        app.run(host='0.0.0.0', threaded=True)

    def start_thread(self):
        # Define a thread for FPV and OpenCV
        thread = threading.Thread(target=self.thread)
        # 'True' means it is a front thread,it would close when the mainloop() closes
        thread.setDaemon(False)
        thread.start()  # Thread starts


def start_app():
    setup_logging('ai.log')
    logger = logging.getLogger(__name__)
    logger.info('ai_service started')

    flask_app = webapp()
    flask_app.start_thread()
