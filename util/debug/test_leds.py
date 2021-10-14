import time
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT = 3      # Number of LED pixels.
LED_PIN = 12      # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
# True to invert the signal (when using NPN transistor level shift)
LED_INVERT = False
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


class LED:
    def __init__(self):
        self.LED_COUNT = 16      # Number of LED pixels.
        # GPIO pin connected to the pixels (18 uses PWM!).
        self.LED_PIN = 12
        # LED signal frequency in hertz (usually 800khz)
        self.LED_FREQ_HZ = 800000
        # DMA channel to use for generating signal (try 10)
        self.LED_DMA = 10
        self.LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        # True to invert the signal (when using NPN transistor level shift)
        self.LED_INVERT = False
        self.LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--clear', action='store_true',
                            help='clear the display on exit')
        args = parser.parse_args()

        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(self.LED_COUNT, self.LED_PIN, self.LED_FREQ_HZ,
                                       self.LED_DMA, self.LED_INVERT, self.LED_BRIGHTNESS, self.LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()

    # Define functions which animate LEDs in various ways.
    def colorWipe(self, R, G, B):
        """Wipe color across display a pixel at a time."""
        color = Color(R, G, B)
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()

    def fade(self, from_r, from_g, from_b, to_r, to_g, to_b, steps, duration):
        r_inc = (from_r - to_r) / steps
        g_inc = (from_g - to_g) / steps
        b_inc = (from_b - to_b) / steps

        r = from_r
        g = from_g
        b = from_b

        for i in range(steps):
            r -= r_inc
            g -= g_inc
            b -= b_inc
            self.colorWipe(int(r), int(g), int(b))
            time.sleep(duration / steps)


if __name__ == '__main__':
    led = LED()
    while True:
        led.colorWipe(255, 0, 0)  # red
        time.sleep(.25)
        led.colorWipe(0, 0, 0)
        time.sleep(.1)
        led.colorWipe(255, 0, 0)
        led.fade(255, 0, 0, 0, 0, 0, 20, .6)
