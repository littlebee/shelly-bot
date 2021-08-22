

from imutils.video import VideoStream
import imutils
import face_recognition
import cv2
import time

vs = VideoStream(usePiCamera=True).start()
time.sleep(2)

print('Face Detection running')
print('(press ctrl+C to stop)')

frameCount = 0
startTime = time.time()

try:
    while True:
        frame = vs.read()
        # frame = imutils.resize(frame, width=500)
        frameCount += 1

        # Find all the faces in the current frame of video
        face_locations = face_recognition.face_locations(frame)

        # Display the results
        for top, right, bottom, left in face_locations:
            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Display the resulting image
        cv2.imshow('Face detection running', frame)

        # TODO: why is this necessary?  Without it, imshow doesn't show anything
        if cv2.waitKey(1) == 13:
            break

except KeyboardInterrupt:
    print("")
    pass

totalTime = time.time() - startTime

vs.stop()
cv2.destroyAllWindows()


print(f"total time: {totalTime}")
print(f"total frames: {frameCount}")
print(f"FPS: {frameCount / totalTime}")
