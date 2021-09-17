#!/usr/bin/env python3

import cv2
import glob
import re

rex = re.compile("\d+")

for cameraDevice in glob.glob("/dev/video?"):
    print(f"{cameraDevice}")
    m = rex.search(cameraDevice)
    devNum = m.group()
    print(f"attempting to open {devNum}")
    c = cv2.VideoCapture(int(devNum))
    print("VideoCapture returned")
    if c.isOpened():
        print(f"found camera device: {camera}")
        pass
