
#/bin/sh
# this script is meant to be run from your local development machine.


if [ "$1" == "" ]; then
  echo "Error: missing parameter.  usage: sbin/upload.sh IP_ADDRESS_OR_NAME"
  exit 1
fi

set -x

TARGET_DIR="/home/pi/shelly-bot"
TARGET_HOST=$1

ssh $TARGET_HOST "mkdir -p $TARGET_DIR"

scp -r ./src/engagement_service $TARGET_HOST:$TARGET_DIR
scp -r ./src/common $TARGET_HOST:$TARGET_DIR
scp -r ./util $TARGET_HOST:$TARGET_DIR
scp -r ./sbin $TARGET_HOST:$TARGET_DIR
scp -r ./media $TARGET_HOST:$TARGET_DIR

scp -r ./run-engagement.py $TARGET_HOST:$TARGET_DIR
scp -r ./sbin/setup/engagement.sh $TARGET_HOST:$TARGET_DIR/setup-engagement.sh
