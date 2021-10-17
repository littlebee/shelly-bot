"""

This class provides methods for speaking to the humans.
"""
import os
import time
import subprocess
import random

import paths

ESPEAK_CMD = "espeak -v en+f2"
ESPEAK_AFFIX = "--stdout | aplay"

GREETINGS = [
    ["Hello", None],
    ["Yo!", "what up?"],
    ["Hi", "good to see you"],
    ["What are you doing, ", None],
    [None, "...my huuman.  What up?"],
    ["Yo, ", "...looking good, darling."]
]
INTRODUCTIONS = [
    "Oh, hello.  What is your name?",
    "Hello, I did not see you there. What is your name?",
    "Hi, my name is Shelly bot, what is your name?"
]

POSES = [
    "Pose for me.  Let me behold your beauty.",
    "You are fierce.",
    "Yaaaas, the camera loves you darling.",
    "Make love to the camera.",
    "You're a tiger. Yaaaas."
    "You're a lemur; cute and cuddly with sharp fierce claws",
    "You're happy.  You're sad.  You couldn't give a rats ass.",
    "Make love to my cold electronic eye.  Yaaaassss.",
    "Strike a pose, let's get down to it.",
    "Give me fierce, yaaaas."
]

REJECTIONS = [
    "Well FINE.  Be that way then.",
    "I didn't want to be her friend anyway.",
    "Ok, well see if I remember you.  not."
]

BOREDOM = [
    "Yawn, I'm bored.",
    "Well this is fun isn't it?",
    "I might as well take a nap",
    "If only someone would be my friend"
]

MIN_SECONDS_BETWEEN_GREETINGS = 120


def async_cmd(cmd):
    subprocess.Popen(
        [cmd],
        shell=True,
        stdin=None,
        stdout=None,
        stderr=None,
        close_fds=True
    )


def name_wav_file_path(name):
    return f"data/faces/{name}/name.wav"


def play_name_cmd(name):
    return f"aplay {name_wav_file_path(name)}"


def play_name(name):
    os.system(play_name_cmd(name))


def play_camera_snap():
    async_cmd(f"aplay media/sounds/camera_snap.wav")


def espeak_cmd(text):
    return f"{ESPEAK_CMD} \"{text}\" {ESPEAK_AFFIX}"


def say(text):
    os.system(espeak_cmd(text))


def say_async(text):
    async_cmd(espeak_cmd(text))


def say_random_from(collection, runAsync=False):
    msg = collection[random.randrange(
        len(collection))]
    if runAsync:
        say_async(msg)
    else:
        say(msg)


# kv of "name": timeLastGreeted
_lastTimeGreeted = {}


def say_hello(names):
    greeting = GREETINGS[random.randrange(
        len(GREETINGS))]

    names_to_greet = []
    for name in names:
        if name in _lastTimeGreeted and \
           time.time() - _lastTimeGreeted[name] < MIN_SECONDS_BETWEEN_GREETINGS:
            continue
        elif name not in names_to_greet:
            names_to_greet.append(name)

    if len(names_to_greet) == 0:
        return

    if greeting[0]:
        say(greeting[0])

    for name in names_to_greet:
        play_name(name)
        _lastTimeGreeted[name] = time.time()

    if greeting[1]:
        say(greeting[1])

    print(f"greeted {names_to_greet}")


def introduce_yourself():
    say_random_from(INTRODUCTIONS)


def request_name_again():
    say("I'm sorry, I didn't hear that. Please say your name.")


def let_me_get_a_look_at_you():
    say("Let me get a good look at you")


def where_did_you_go():
    say("Where did you go?  Let me get a good look at you.")


def pose_for_me():
    say_random_from(POSES)


def and_im_spent():
    say_async("...and I'm spent.")


def nice_to_meet_you(name):
    say("It was nice to meet you...")
    play_name(name)
    say("... I will try and remember your name.")


def rejection():
    say_random_from(REJECTIONS)


def i_need_a_nap():
    say("I'm tired and need to nap now.")


_last_time_bored = time.time()
MIN_BORED_DELAY = 20


def im_bored():
    global _last_time_bored
    current_time = time.time()
    if current_time - _last_time_bored > MIN_BORED_DELAY:
        _last_time_bored = current_time
        say_random_from(BOREDOM)
