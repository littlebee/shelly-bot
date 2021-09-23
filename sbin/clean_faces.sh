#!/bin/sh

set -x

rm -Rf data/faces/face*
rm -f data/faces_processed.json
rm -f data/encodings.pickle

python3 src/server/retrain_model.py