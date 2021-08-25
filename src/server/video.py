import threading
import base64

import cv2
import zmq
import picamera
from picamera.array import PiRGBArray

# pid = PID.PID()
# pid.SetKp(0.5)
# pid.SetKd(0)
# pid.SetKi(0)

Y_lock = 0
X_lock = 0
tor = 17


class Video:
    def __init__(self):
        self.frame_num = 0
        self.fps = 0

        self.colorUpper = (44, 255, 255)
        self.colorLower = (24, 100, 100)

    def SetIP(self, invar):
        self.IP = invar

    def capture_thread(self, IPinver):
        # font = cv2.FONT_HERSHEY_SIMPLEX

        camera = picamera.PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 20
        rawCapture = PiRGBArray(camera, size=(640, 480))

        context = zmq.Context()
        footageSocket = context.socket(zmq.PUB)
        footageSocket.connect('tcp://%s:5555' % IPinver)

        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            frame_image = frame.array
            cv2.line(frame_image, (300, 240), (340, 240), (128, 255, 128), 1)
            cv2.line(frame_image, (320, 220), (320, 260), (128, 255, 128), 1)

            encoded, buffer = cv2.imencode('.jpg', frame_image)
            jpg_as_text = base64.b64encode(buffer)
            footageSocket.send(jpg_as_text)

            rawCapture.truncate(0)


def start_video_thread(addr):
    def video_thread_func():
        video = Video()
        video.capture_thread(addr[0])

    video_thread = threading.Thread(target=video_thread_func)
    # 'True' means it is a front thread,it would close when the mainloop() closes
    video_thread.setDaemon(True)
    video_thread.start()  # Thread starts


if __name__ == '__main__':
    video = Video()
    while 1:
        video.capture_thread('192.168.0.110')
        pass
