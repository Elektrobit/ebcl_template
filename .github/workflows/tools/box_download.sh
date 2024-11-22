#!/bin/bash

MAX_RETRIES=10
DELAY=60
ARCH=$1

sudo apt update
source /build/venv/bin/activate

for i in $(seq 1 $MAX_RETRIES); do
OUTPUT=$(kiwi-ng system boxbuild --box ubuntu --$ARCH -- --description /tmp --target-dir /tmp/noImage 2>&1)

  if echo "$OUTPUT" | grep -q "Connection reset"; then
    echo "Attempt $i failed due to 'Connection reset by peer'! Retrying in $DELAY seconds..."
    sleep $DELAY
  else
    echo "Command succeeded or failed for another reason:"
    echo "$OUTPUT"
    break
  fi
done