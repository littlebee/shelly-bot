import threading
import face_recognition

lock = threading.Lock()


# I was getting terrible performance when the engagement
# thread and face_detect thread were both calling the
# face_recognition.   Putting a lock around these restored
# 3-5 fps to the capture rate.
#
# I'm not sure if a.) Python's threading model is weak,
# b.) face_recognition is not thread safe, or c.) I am
# using shared memory poorly and that is causing some
# thrash or unnecessary locking in python :shrug:
#
# I have other reason to suspect b.)   See comments on
# this commit
#    https://github.com/littlebee/shelly-bot/commit/0fd3c80f1433fbf532a85eb5666b2c6df616b617
# The seg fault was fixed by spawning retrain_model.py into a process.
#
#

def face_encodings(frame, faces):
    lock.acquire()
    face_encodings = face_recognition.face_encodings(frame, faces)
    lock.release()
    return face_encodings


def compare_faces(encoding_data, encoding):
    lock.acquire()
    matches = face_recognition.compare_faces(encoding_data, encoding)
    lock.release()
    return matches


def face_locations(frame):
    lock.acquire()
    faces = face_recognition.face_locations(frame)
    lock.release()
    return faces
