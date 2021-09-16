#!/usr/bin/env python3

import os
from imutils.video import VideoStream
import face_recognition
import cv2
import time
import picamera
import argparse
from picamera.array import PiRGBArray
import numpy as np

CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480

os.environ["DISPLAY"] = ":0.0"

parser = argparse.ArgumentParser()
parser.add_argument('--imutilsVideo',
                    help='Use imutils.video instead of picamera package to capture video',
                    dest='useImutilsVideo',
                    action='store_true')
args = parser.parse_args()

vs = None
if args.useImutilsVideo:
    print('Using imutils.video to caption image stream')
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2)
else:
    print('Using picamera package to caption image stream')
    camera = picamera.PiCamera()
    camera.resolution = (CAPTURE_WIDTH, CAPTURE_HEIGHT)
    # camera.framerate = 20
    rawCapture = PiRGBArray(camera, size=(CAPTURE_WIDTH, CAPTURE_HEIGHT))

print('Face Detection running')
print('(press ctrl+C to stop)')

frameCount = 0
startTime = time.time()
last_dimensions = {}


def process_frame(frameImage):
    global frameCount
    global last_dimensions

    frameCount += 1
    last_dimensions = {
        "height": np.size(frameImage, 0),
        "width": np.size(frameImage, 1)
    }

    # Find all the faces in the current frame of video
    face_locations = face_recognition.face_locations(frameImage)

    # Display the results
    for top, right, bottom, left in face_locations:
        # Draw a box around the face
        cv2.rectangle(frameImage, (left, top),
                      (right, bottom), (0, 0, 255), 2)

    # Display the resulting image
    cv2.imshow('Face detection running', frameImage)

    # TODO: why is this necessary?  Without it, imshow doesn't show anything
    cv2.waitKey(1)


try:
    if args.useImutilsVideo:
        while True:
            frame = vs.read()
            process_frame(frame)
    else:
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            process_frame(frame.array)
            rawCapture.truncate(0)


except KeyboardInterrupt:
    print("")
    pass

totalTime = time.time() - startTime

# vs.stop()
cv2.destroyAllWindows()


print(f"last_dimensions: {last_dimensions}")
print(f"total time: {totalTime}")
print(f"total frames: {frameCount}")
print(f"FPS: {frameCount / totalTime}")
