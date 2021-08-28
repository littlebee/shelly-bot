import os
import threading
import datetime
import numpy as np
import cv2

from base_camera import BaseCamera

CVRun = 1
lineColorSet = 255
frameRender = 1
findLineError = 20

ImgIsNone = 0

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])


class CVThread(threading.Thread):
    font = cv2.FONT_HERSHEY_SIMPLEX

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.CVMode = 'none'
        self.imgCV = None

        self.radius = 0
        self.box_x = None
        self.box_y = None
        self.drawing = 0

        self.findColorDetection = 0

        super(CVThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

        self.avg = None
        self.motionCounter = 0
        self.lastMovtionCaptured = datetime.datetime.now()
        self.frameDelta = None
        self.thresh = None
        self.cnts = None

    def mode(self, invar, imgInput):
        self.CVMode = invar
        self.imgCV = imgInput
        self.resume()

    def elementDraw(self, imgInput):
        if self.CVMode == 'none':
            pass

        elif self.CVMode == 'findColor':
            if self.findColorDetection:
                cv2.putText(imgInput, 'Target Detected', (40, 60),
                            CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                self.drawing = 1
            else:
                cv2.putText(imgInput, 'Target Detecting', (40, 60),
                            CVThread.font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                self.drawing = 0

            if self.radius > 10 and self.drawing:
                cv2.rectangle(imgInput, (int(self.box_x-self.radius), int(self.box_y+self.radius)),
                              (int(self.box_x+self.radius), int(self.box_y-self.radius)), (255, 255, 255), 1)

        return imgInput

    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def run(self):
        while 1:
            self.__flag.wait()
            if self.CVMode == 'none':
                continue
            elif self.CVMode == 'findColor':
                self.CVThreading = 1
                self.findColor(self.imgCV)
                self.CVThreading = 0
            pass


class Camera(BaseCamera):
    video_source = 0
    modeSelect = 'none'
    # modeSelect = 'findlineCV'
    # modeSelect = 'findColor'
    # modeSelect = 'watchDog'

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    def colorFindSet(self, invarH, invarS, invarV):
        global colorUpper, colorLower
        HUE_1 = invarH+15
        HUE_2 = invarH-15
        if HUE_1 > 180:
            HUE_1 = 180
        if HUE_2 < 0:
            HUE_2 = 0

        SAT_1 = invarS+150
        SAT_2 = invarS-150
        if SAT_1 > 255:
            SAT_1 = 255
        if SAT_2 < 0:
            SAT_2 = 0

        VAL_1 = invarV+150
        VAL_2 = invarV-150
        if VAL_1 > 255:
            VAL_1 = 255
        if VAL_2 < 0:
            VAL_2 = 0

        colorUpper = np.array([HUE_1, SAT_1, VAL_1])
        colorLower = np.array([HUE_2, SAT_2, VAL_2])
        print('HSV_1:%d %d %d' % (HUE_1, SAT_1, VAL_1))
        print('HSV_2:%d %d %d' % (HUE_2, SAT_2, VAL_2))
        print(colorUpper)
        print(colorLower)

    def modeSet(self, invar):
        Camera.modeSelect = invar

    def CVRunSet(self, invar):
        global CVRun
        CVRun = invar

    def colorSet(self, invar):
        global lineColorSet
        lineColorSet = invar

    def randerSet(self, invar):
        global frameRender
        frameRender = invar

    def errorSet(self, invar):
        global findLineError
        findLineError = invar

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        print('initializing VideoCapture')
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        cvt = CVThread()
        cvt.start()

        while True:
            # read current frame
            _, img = camera.read()
            if img is None:
                if ImgIsNone == 0:
                    print(
                        "The camera has not read data, please check whether the camera can be used normally.")
                    print(
                        "Use the command: 'raspistill -t 1000 -o image.jpg' to check whether the camera can be used correctly.")
                    ImgIsNone = 1
                continue

            if Camera.modeSelect == 'none':
                cvt.pause()
            else:
                if cvt.CVThreading:
                    pass
                else:
                    cvt.mode(Camera.modeSelect, img)
                    cvt.resume()
                try:
                    img = cvt.elementDraw(img)
                except:
                    pass

            # encode as a jpeg image and return it
            if cv2.imencode('.jpg', img)[0]:
                yield cv2.imencode('.jpg', img)[1].tobytes()
