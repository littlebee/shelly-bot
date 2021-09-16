"""

This class watches for updated encodings .pickle file from from retraining
process and loads the new encodings.

"""
import os
import sys
import time
import threading
import pickle

from event import Event

ENCODINGS_FILE_PATH = "data/encodings.pickle"


class EncodingsFile:
    thread = None  # background thread that reads faces detected
    times_read = 0
    started_at = 0
    encodings_data = None
    last_modified = None

    def __init__(self):
        if EncodingsFile.thread is None:
            EncodingsFile.thread = threading.Thread(target=self._thread)
            EncodingsFile.thread.start()

    def get_encodings_data(self):
        return EncodingsFile.encodings_data

    @classmethod
    def _thread(cls):
        print('Starting encoding file watch thread.')
        EncodingsFile.started_at = time.time()

        while True:
            EncodingsFile.load_encodings_file_if_modified()
            time.sleep(1)

    @classmethod
    def load_encodings_file_if_modified(cls):
        last_modified = os.path.getmtime(ENCODINGS_FILE_PATH)
        if last_modified != EncodingsFile.last_modified:
            EncodingsFile.load_encodings_file()

    @classmethod
    def load_encodings_file(cls):
        encodings_data = None
        EncodingsFile.last_modified = os.path.getmtime(ENCODINGS_FILE_PATH)
        encodings_data = pickle.loads(
            open(ENCODINGS_FILE_PATH, "rb").read(), encoding='latin1')

        EncodingsFile.times_read += 1
        EncodingsFile.encodings_data = encodings_data
        print(f"EncodingsFile updated from {ENCODINGS_FILE_PATH}")
