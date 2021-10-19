"""
This was originally pilfered from
https://github.com/adeept/Adeept_RaspTank/blob/a6c45e8cc7df620ad8977845eda2b839647d5a83/server/base_camera.py

 Which looks like it was in turn pilfered from
 https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited

"Great artists steal". Thank you, @adeept and @miguelgrinberg!
"""
import time
import threading
import cv2


# last n seconds to use for fps calc
FPS_WINDOW = 60


class BaseCamera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    frames_read = 0
    started_at = 0

    fps_frames_read = 0
    fps_started_at = 0
    last_fps = 0

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()

            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access = time.time()

        return BaseCamera.frame

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def stats(cls):
        now = time.time()
        total_time = now - cls.started_at
        return {
            "totalFramesRead": cls.frames_read,
            "totalTime": total_time,
            "overallFps": cls.frames_read / total_time,
            "fpsStartedAt": cls.fps_started_at,
            "floatingFps": cls.last_fps
        }

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting camera thread.')
        BaseCamera.started_at = time.time()
        BaseCamera.fps_started_at = time.time()

        frames_iterator = cls.frames()

        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.frames_read += 1

            BaseCamera.fps_frames_read += 1
            now = time.time()
            fps_time = now - BaseCamera.fps_started_at
            if fps_time > FPS_WINDOW:
                BaseCamera.last_fps = BaseCamera.fps_frames_read / fps_time
                BaseCamera.fps_started_at = time.time()
                BaseCamera.fps_frames_read = 0

            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            # if time.time() - BaseCamera.last_access > 10:
            #     frames_iterator.close()
            #     print('Stopping camera thread due to inactivity.')
            #     break
        BaseCamera.thread = None
