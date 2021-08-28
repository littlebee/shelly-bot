
# this script is meant to be run from your local development machine.


if [ "$1" == "" ]; then
  echo "Error: missing parameter.  usage: sbin/upload.sh IP_ADDRESS_OR_NAME"
  exit 1
fi

set -x

TARGET_DIR="/home/pi/shelly-bot"
TARGET_HOST=$1
TMP_DIR="/tmp/shelly-bot"

ssh $TARGET_HOST "mkdir -p $TARGET_DIR"

scp -r ./src $TARGET_HOST:$TARGET_DIR
scp -r ./util $TARGET_HOST:$TARGET_DIR
scp -r ./sbin $TARGET_HOST:$TARGET_DIR
scp -r ./dist $TARGET_HOST:$TARGET_DIR
