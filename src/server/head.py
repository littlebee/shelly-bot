#!/usr/bin/env python3

import sys
import time
import threading
import random

from adafruit_servokit import ServoKit

# index in Head.motors
PAN_MOTOR = 0
TILT_MOTOR = 1

PAN_CHANNEL = 14
TILT_CHANNEL = 15

PAN_MIN = 50
PAN_CENTER = 70
PAN_MAX = 100

TILT_MIN = 140
TILT_CENTER = 150
TILT_MAX = 160

STEP_DEGREES = 10
STEP_DELAY = .1

MIN_SCAN_DELAY = 10


servo_kit = ServoKit(channels=16)


def limit_angle(motor, angle):
    limited_angle = angle
    min_angle = motor['min_angle']
    max_angle = motor['max_angle']
    if angle < min_angle:
        limited_angle = min_angle
    elif angle > max_angle:
        limited_angle = max_angle

    return limited_angle


class Head:
    thread = None  # background thread that reads frames from camera
    pause_event = threading.Event()
    force_stop = False

    motors = [{
        'channel': PAN_CHANNEL,
        'current_angle': PAN_CENTER,
        'dest_angle': PAN_CENTER,
        'step_degrees': 10,
        'step_delay': .15,
        'stopped_event': threading.Event(),
        'max_angle': PAN_MAX,
        'min_angle': PAN_MIN,
        'center_angle': PAN_CENTER
    }, {
        'channel': TILT_CHANNEL,
        'current_angle': TILT_CENTER,
        'dest_angle': TILT_CENTER,
        'step_degrees': 10,
        'step_delay': .1,
        'stopped_event': threading.Event(),
        'max_angle': TILT_MAX,
        'min_angle': TILT_MIN,
        'center_angle': TILT_CENTER
    }]

    def __init__(self):
        if Head.thread is None:
            Head.thread = threading.Thread(target=self._thread)
            Head.thread.start()

        self.lastScan = time.time()

    def pause(self):
        Head.pause_event.clear()

    def resume(self):
        Head.pause_event.set()

    def center_head(self):
        self.pan_to(PAN_CENTER)
        self.tilt_to(TILT_CENTER)

    def move_to(self, motor, angle):
        new_angle = limit_angle(motor, angle)
        motor['dest_angle'] = new_angle
        self.resume()

    def pan(self, relativeDegrees):
        motor = Head.motors[PAN_MOTOR]
        self.move_to(motor, motor['current_angle'] + relativeDegrees)

    def pan_to(self, angle):
        motor = Head.motors[PAN_MOTOR]
        self.move_to(motor, angle)

    def tilt(self, relativeDegrees):
        motor = Head.motors[TILT_MOTOR]
        self.move_to(motor, motor['current_angle'] + relativeDegrees)

    def tilt_to(self, angle):
        motor = Head.motors[TILT_MOTOR]
        self.move_to(motor, angle)

    def scan(self):
        now = time.time()
        if now - self.lastScan < MIN_SCAN_DELAY:
            return
        self.lastScan = now
        for motor in Head.motors:
            self.move_to(motor, random.randrange(
                motor['min_angle'], motor['max_angle']))

    def sleep(self):
        self.center_head()
        self.tilt_to(TILT_MIN)

    def wait_for_motor_stopped(self, motor):
        motor['stopped_event'].wait()

    def wait_for_pan(self):
        self.wait_for_motor_stopped(Head.motors[PAN_MOTOR])

    def wait_for_tilt(self):
        self.wait_for_motor_stopped(Head.motors[TILT_MOTOR])

    def stop_thread(self):
        Head.force_stop = True

    # The servo motors & gearing for shelly-bot's neck ended up
    # being way too fast and jerky.  This is a hacky attempt
    # to slow it down to about 180deg in 3 seconds versus 1 sec

    @classmethod
    def _thread(cls):
        print('Starting head movement thread.')
        cls.started_at = time.time()

        # have to directly set the first angles so we know
        # where they are positioned
        for motor in cls.motors:
            servo_kit.servo[motor['channel']].angle = motor['center_angle']

        # start running
        cls.pause_event.set()
        while not cls.force_stop:
            cls.pause_event.wait()
            print("moving head")
            did_move = False
            for motor in cls.motors:
                current_angle = motor['current_angle']
                dest_angle = motor['dest_angle']
                direction = 1
                print(
                    f"motor {motor['channel']} current {current_angle} dest {dest_angle}")
                if current_angle > dest_angle:
                    direction = -1
                would_overshoot = cls._step_would_overshoot_dest(
                    motor, direction)
                if current_angle != dest_angle and not would_overshoot:
                    motor['stopped_event'].clear()
                    did_move = True
                    cls._step_move(motor, direction)
                else:
                    motor['stopped_event'].set()

            if not did_move:
                cls.pause_event.clear()

            time.sleep(0)

    @ classmethod
    def _step_move(cls, motor, direction):
        ''' direction = -1 = left; 1 = right '''
        current_angle = motor['current_angle']
        dest_angle = motor['dest_angle']
        new_angle = limit_angle(
            motor,
            current_angle + motor['step_degrees'] * direction)

        if current_angle == new_angle or current_angle == dest_angle:
            return

        print(
            f"stepping motor {motor['channel']}, {direction}, {current_angle}, {new_angle}")
        servo_kit.servo[motor['channel']].angle = new_angle
        time.sleep(motor['step_delay'])
        motor['current_angle'] = new_angle
        return

    @ classmethod
    def _step_would_overshoot_dest(cls, motor, direction):
        current_angle = motor['current_angle']
        dest_angle = motor['dest_angle']
        new_angle = limit_angle(motor,
                                current_angle + motor['step_degrees'] * direction)
        return (direction == -1 and new_angle <
                dest_angle) or (direction == 1 and new_angle > dest_angle)


if __name__ == '__main__':
    head = Head()

    try:
        while True:
            print('Ctrl+c to quit')
            for motor in Head.motors:
                test_angles = [motor['min_angle'],
                               motor['max_angle'], motor['center_angle']]
                for angle in test_angles:
                    print(f"channel {motor['channel']} to {angle}deg")
                    head.move_to(motor, angle)
                    print(f"waiting for motor stopped event")
                    head.wait_for_motor_stopped(motor)

    except KeyboardInterrupt:
        head.stop_thread()

        head = Head()
        head.center_head()
        head.stop_thread()
