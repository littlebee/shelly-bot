"""

This class provides methods for speaking to the humans.
"""
import os
import random

ESPEAK_CMD = "espeak -v en+f2"

GREETINGS = [
    ["Hello", None],
    ["Yo!", "what up, G?"],
    ["Hi", None],
    ["What are you doing", None],
    [None, ", my human.  What up?"]
]
INTRODUCTIONS = [
    "Oh, hello.  What is your name?",
    "Hello, I did not see you there. What is your name?",
    "Hi, my name is Shelly bot, what is your name?"
]


def espeak_cmd(text):
    return f"{ESPEAK_CMD} \"{text}\""


class Speech:

    @classmethod
    def say_hello(cls, name):
        greeting = GREETINGS[random.randrange(
            len(GREETINGS))]
        name_wav_file_path = f"data/faces/{name}/name.wav"
        cmd = f"{espeak_cmd(greeting[0])}  && aplay {name_wav_file_path} && {espeak_cmd(greeting[1])}"
        os.system(cmd)
        print(f"greeted {name}")

    @classmethod
    def introduce_yourself(cls):
        intro = INTRODUCTIONS[random.randrange(
            len(INTRODUCTIONS))]
        os.system(espeak_cmd(intro))

    @classmethod
    def request_name_again(cls):
        os.system(espeak_cmd(
            "I'm sorry, I didn't hear that. Please say your name."))
