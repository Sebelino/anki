#!/usr/bin/env bash

set -Eeuo pipefail

filename="$1"
tmpfile="$(mktemp).mp3"

speed=1.5

ffmpeg -i "$filename" -filter:a "atempo=${speed}" "$tmpfile"
mv "$tmpfile" "$filename"
