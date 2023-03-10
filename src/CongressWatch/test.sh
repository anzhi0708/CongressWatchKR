#!/usr/bin/env bash
#

TARGET_DIR=$1

echo PID: $$
echo TARGET_DIR: $TARGET_DIR

if [[ "$TARGET_DIR" == "" ]]; then
	echo Invalid Argument: No argument provided
	exit -1
fi

./_test.py $1 1> /dev/null

