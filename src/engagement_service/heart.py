"""
This class detects faces in frames it gets from the camera object passed to
the constructor.

The get_faces method returns the bounding boxes for all faces last detected.

A thread is created that does the heavy lifting of detecting faces and updates
a class var that contains the last faces detected. This allows the thread providing
the video feed to stream at 30fps while face frames lag behind at 3fps (maybe upto 10?)
"""
import sys
import time
import threading
import logging

from rpi_ws281x import PixelStrip

logger = logging.getLogger(__name__)

PINK = (168, 50, 105)
RED = (255, 0, 0)
BLUE = (0, 0, 128)
BLACK = (0, 0, 0)

BPM_NORMAL = 60
BPM_SLEEPING = 40
BPM_EXCITED = 110

LED_COUNT = 16      # Number of LED pixels.
LED_PIN = 12      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class Heart:
    thread = None
    color = BLACK  # background thread that reads frames from camera
    next_color = PINK
    bpm = 60

    strip = None

    def __init__(self):
        if Heart.thread is None:
            Heart.thread = threading.Thread(target=self._thread)
            Heart.thread.start()

        if Heart.strip is None:
            Heart.strip = PixelStrip(
                LED_COUNT,
                LED_PIN,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                LED_BRIGHTNESS,
                LED_CHANNEL
            )
            Heart.strip.begin()

    def pink(self):
        Heart.next_color = PINK
        return self

    def red(self):
        Heart.next_color = RED
        return self

    def blue(self):
        Heart.next_color = BLUE
        return self

    def normal(self):
        Heart.bpm = BPM_NORMAL
        return self

    def sleeping(self):
        Heart.bpm = BPM_SLEEPING
        return self

    def excited(self):
        Heart.bmp = BPM_EXCITED
        return self

    @classmethod
    def _thread(cls):
        logger.info('Starting heart thread.')
        cls.started_at = time.time()

        while True:
            # logger.info(f"heart bpm: {cls.bpm}")
            bps = cls.bpm / 60

            if cls.next_color != cls.color:
                cls.fadeTo(cls.next_color, 40, 1)
                cls.color = cls.next_color

            # simulate heartbeat
            cls.fill(cls.color)  # red
            time.sleep(.25 / bps)
            cls.fill(BLACK)
            time.sleep(.1 / bps)
            cls.fill(cls.color)
            cls.fadeTo(BLACK, 20, .6 / bps)

    @classmethod
    def fill(cls, rgb):
        (r, g, b) = rgb
        for i in range(cls.strip.numPixels()):
            cls.strip.setPixelColorRGB(i, r, g, b, 255)
            cls.strip.show()

    # fade from current color to rgb

    @ classmethod
    def fadeTo(cls, rgb, steps, duration):
        (r1, g1, b1) = cls.color
        (r2, g2, b2) = rgb
        r_inc = (r1 - r2) / steps
        g_inc = (g1 - g2) / steps
        b_inc = (b1 - b2) / steps

        r = r1
        g = g1
        b = b1

        for i in range(steps):
            r -= r_inc
            g -= g_inc
            b -= b_inc
            cls.fill((int(r), int(g), int(b)))
            time.sleep(duration / steps)
