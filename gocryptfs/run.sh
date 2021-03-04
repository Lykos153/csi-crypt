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
  fusermount -u "$TARGET_PATH"
}

trap _term SIGTERM
trap _term SIGINT


if [ ! -e "$SOURCE_PATH/gocryptfs.conf" ]; then
    echo "Initialising backend"
    printf "$ENCRYPTION_KEY" | gocryptfs -init "$SOURCE_PATH" >/dev/null
fi

echo "Publishing volume to $TARGET_PATH"
mkdir -p "$TARGET_PATH"
printf "$ENCRYPTION_KEY" | gocryptfs -f "$SOURCE_PATH" "$TARGET_PATH"& \
wait $!
ret=$?
if [ $ret -ne 0 ]; then
    echo "ERROR publishing volume"
fi
exit $ret

