# /usr/bin/env python3
import os
import pickle
import face_recognition
import cv2
from imutils import paths as imutils_paths

import paths


def retrain_model():
    imagePaths = list(imutils_paths.list_images(paths.FACES_DATA_DIR))

    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("trainer: processing image {}/{}".format(i + 1,
                                                       len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        # images are already cropped to a single face
        image = cv2.imread(imagePath)
        # convert from BGR (OpenCV ordering) to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

    new_encodings_data = {"encodings": knownEncodings, "names": knownNames}

    # save encodings data in pickle file for faster start up
    f = open(paths.ENCODINGS_FILE_PATH, "wb")
    f.write(pickle.dumps(new_encodings_data))
    f.close()


if __name__ == '__main__':
    retrain_model()
