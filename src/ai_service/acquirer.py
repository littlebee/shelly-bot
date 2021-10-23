"""
This class detects faces in frames it gets from the camera object passed to
the constructor.

The get_faces method returns the bounding boxes for all faces last detected.

A thread is created that does the heavy lifting of detecting faces and updates
a class var that contains the last faces detected. This allows the thread providing
the video feed to stream at 30fps while face frames lag behind at 3fps (maybe upto 10?)
"""
import os
import time
import threading
import base64
import glob
import cv2

import paths

RECORD_COMMAND = f"arecord -d 3 -D hw:2,0 -c 2 -r 32000 -f S16_LE {paths.TMP_RAW_NAME_FILE}"
FFMPEG_COMMAND = f"ffmpeg -i {paths.TMP_RAW_NAME_FILE} -af silenceremove=stop_periods=-1:stop_duration=0.1:stop_threshold=-40dB -y {paths.TMP_NAME_FILE}"
# minimum number of bytes of mp3, after removing silence, that we will accept
RECORDING_SIZE_MINIMUM = 2600


class Acquirer:
    thread = None  # background thread that reads frames from camera
    camera = None

    acquire_duration = 10  # seconds
    acquire_event = threading.Event()
    is_acquiring = False

    new_frames_saved = 0

    def __init__(self, camera):
        Acquirer.camera = camera
        if Acquirer.thread is None:
            Acquirer.thread = threading.Thread(target=self._thread)
            Acquirer.thread.start()

    def augment_frame(self, frame):
        color = (0, 255, 0)
        if Acquirer.is_acquiring:
            cv2.putText(
                frame,
                "Making new friend",
                (5, 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                .4, color, 1)
        return frame

    def get_names(self):
        names = []
        for path in glob.iglob(f"{paths.FACES_DATA_DIR}/**/name.mp3"):
            print(f"got path {path}")
            name = path.split(os.path.sep)[-2]
            content = None
            with open(path, 'rb') as file:
                content = file.read()
                print(f"read {len(content)}bytes of mp3")
                b64bytes = base64.b64encode(content)
                content = b64bytes.decode()

            names.append({
                "name": name,
                "content": content
            })

        return names

    def new_face(self):
        Acquirer.new_frames_saved = 0
        # if save_face is never called then there may be files
        # in the TMP_DATA_DIR. delete and recreate it
        os.system(f"rm -Rf {paths.TMP_DATA_DIR}")
        os.system(f"mkdir -p {paths.TMP_DATA_DIR}")

    def acquire_spoken_name(self):
        os.system(f"{RECORD_COMMAND} && {FFMPEG_COMMAND}")
        with open(paths.TMP_NAME_FILE, 'rb') as file:
            content = file.read()
            length = len(content)
            print(f"acquired {length}bytes of mp3")
            if length < RECORDING_SIZE_MINIMUM:
                return None

            b64bytes = base64.b64encode(content)
            return b64bytes.decode()

    def acquire_images(self):
        # kick start thread
        Acquirer.acquire_event.set()

    def save_new_face(self):
        face_number = len(os.listdir(paths.FACES_DATA_DIR))
        new_face_name = f"face_{face_number}"
        new_face_path = f"{paths.FACES_DATA_DIR}/{new_face_name}"
        os.system(f"mv {paths.TMP_DATA_DIR} {new_face_path}")
        return new_face_name

    @classmethod
    def stats(cls):
        return {
            "lastDimensions": cls.last_dimensions,
            "fps": cls.fps_stats.stats(),
            "total_faces_detected": cls.total_faces_detected
        }

    @classmethod
    def _thread(cls):
        print('Starting acquisition thread.')

        acquisition_started_at = 0

        while True:
            cls.is_acquiring = False
            cls.acquire_event.wait()
            cls.acquire_event.clear()
            cls.is_acquiring = True
            print(
                f"Acquiring images for new face for {cls.acquire_duration} seconds")
            acquisition_started_at = time.time()

            while time.time() - acquisition_started_at < cls.acquire_duration:
                # get frame, run face detection on it and update Acquirer.last_faces
                frame = cls.camera.get_frame()
                cls.save_image(frame)
                # slow this down to max 10fps for more variation of images
                time.sleep(.1)

    @classmethod
    def save_image(cls, image):
        path = f"{paths.TMP_DATA_DIR}/frame_{cls.new_frames_saved}.jpg"
        cv2.imwrite(path, image)
        print(f"saved face {path}")

        cls.new_frames_saved += 1
