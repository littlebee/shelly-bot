"""

This class provides methods for speaking to the humans.
"""
import os
import random

import paths

ESPEAK_CMD = "espeak -v en+f2"

GREETINGS = [
    ["Hello", None],
    ["Yo!", "what up, G?"],
    ["Hi", None],
    ["What are you doing", None],
    [None, ", my huuman.  What up?"]
]
INTRODUCTIONS = [
    "Oh, hello.  What is your name?",
    "Hello, I did not see you there. What is your name?",
    "Hi, my name is Shelly bot, what is your name?"
]

POSES = [
    "Pose for me.  Let me behold your beauty.  You are fierce."
    "Yaaaas, the camera loves you darling, make love to the camera",
    "You're a tiger. You're a lemur; cute and cuddly with sharp fierce claws",
    "You're happy.  You're sad.  You couldn't give a rats ass.",
    "Make love to my cold electronic eye.  Yaaaassss."
]

REJECTIONS = [
    "Well FINE.  Be that way then.",
    "I didn't want to be her friend anyway.",
    "Ok, well see if I remember you.  not."
]


def name_wav_file_path(name):
    return f"data/faces/{name}/name.wav"


def play_name_cmd(name):
    return f"aplay {name_wav_file_path(name)}"


def play_name(name):
    os.system(play_name_cmd(name))


def play_camera_snap():
    os.system(f"aplay media/sounds/camera_snap.wav")


def espeak_cmd(text):
    return f"{ESPEAK_CMD} \"{text}\""


def say(text):
    os.system(espeak_cmd(text))


def say_random_from(collection):
    intro = collection[random.randrange(
        len(collection))]
    say(intro)


def say_hello(name):
    greeting = GREETINGS[random.randrange(
        len(GREETINGS))]

    say(greeting[0])
    play_name(name)
    say(greeting[1])
    print(f"greeted {name}")


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
    say("...and I'm spent.")


def nice_to_meet_you(name):
    say("It was nice to meet you...")
    play_name(name)
    say("... I will try and remember your name.")


def rejection():
    say_random_from(REJECTIONS)
