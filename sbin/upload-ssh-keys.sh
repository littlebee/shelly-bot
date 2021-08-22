
# This script is meant to be run from your local development machine.
# Run this first to make the other upload script not prompt you for
# your ssh keys.
#
#


if [ "$1" == "" ]; then
  echo "Error: missing parameter.  usage: sbin/upload.sh pi@IP_ADDRESS_OR_NAME"
  exit 1
fi

set -x

TARGET_HOST=$1

# you may need to change this for your public key file if you are on
# windows; named it other than the default or put it somewhere other
# than below.
set +x && echo "You may need to change this" && set -x
SOURCE_PUB_FILE=~/.ssh/id_rsa.pub

cat $SOURCE_PUB_FILE | ssh $TARGET_HOST "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
