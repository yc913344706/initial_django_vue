#!/bin/bash

git log --pretty=format:"%an" --numstat | awk 'BEGIN {current=""} /^[a-zA-Z]/ {current=$0; next} NF==3 {add[current]+=$1; del[current]+=$2} END {for (name in add) printf "%s\t+%d\t-%d\t= %d\n", name, add[name], del[name], add[name]-del[name]}' | sort -k4nr
