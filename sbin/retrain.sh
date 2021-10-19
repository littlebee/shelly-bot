#!/bin/sh

rm -Rf data/encodings.pickle
rm -Rf data/faces_processed.json

python3 src/server/retrain_model.py
