
#/bin/sh
# this script is meant to be run from your local development machine.


if [ "$1" == "" ]; then
  echo "Error: missing parameter.  usage: sbin/upload.sh IP_ADDRESS_OR_NAME"
  exit 1
fi

set -x

TARGET_DIR="/home/pi/shelly-bot"
TARGET_HOST=$1

AI_HOST=bee@10.69.0.2
AI_TARGET_DIR="/home/bee/shelly-bot"

rsync --progress --partial --exclude=node_modules --exclude=data/ --exclude=.git -avz . $TARGET_HOST:$TARGET_DIR

# relay copy to ai service
ssh $TARGET_HOST "cd $TARGET_DIR && rsync --progress --partial --exclude=node_modules --exclude=data/ --exclude=.git -avz . $AI_HOST:$AI_TARGET_DIR"

