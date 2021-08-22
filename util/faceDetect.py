

from imutils.video import VideoStream
import face_recognition
import cv2
import time
import picamera
import argparse
from picamera.array import PiRGBArray

CAPTURE_WIDTH = 320
CAPTURE_HEIGHT = 208

parser = argparse.ArgumentParser()
parser.add_argument('--imutilsVideo',
                    description='Use imutils.video instead of picamera package to capture video'
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


def process_frame(frameImage):
    global frameCount
    frameCount += 1

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


print(f"total time: {totalTime}")
print(f"total frames: {frameCount}")
print(f"FPS: {frameCount / totalTime}")
