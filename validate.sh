#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <input_string>"
    echo "default: n030w4_1_6-2-9-1"
    input="n030w4_1_6-2-9-1"
else
    input="$1"
fi

output=$(python3 payload.py "$input")

$output
