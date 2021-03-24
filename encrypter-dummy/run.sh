#!/bin/sh

if [ -z "$ENCRYPTION_KEY" ]; then
    echo "ENCRYPTION_KEY is not set"
    exit 1
fi

if [ -z "$TARGET_PATH" ]; then
    echo "TARGET_PATH is not set"
    exit 1
fi

if [ -z "$SOURCE_PATH" ]; then
    echo "SOURCE_PATH is not set"
    exit 1
fi


_term() { 
  echo "Caught SIGTERM signal!"
  umount "$TARGET_PATH"
  exit 0
}

trap _term SIGTERM
trap _term SIGINT

echo "WARNING: This is a dummy encrypter meant for testing purposes. IT DOES NOT ENCRYPT ANYTHING!"

echo "Publishing volume to $TARGET_PATH"
mkdir -p "$TARGET_PATH"
mount --bind "$SOURCE_PATH" "$TARGET_PATH"
ret=$?
if [ $ret -ne 0 ]; then
    echo "mount returned with $ret"
    exit $ret
fi

while true; do
    sleep 3600
done
