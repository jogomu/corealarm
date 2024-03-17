#!/bin/bash

args=("$@")
default_values=(97.5 99 65 97)

while true; do
    # ensure we have at least one line to pass to corealarm.py
    tail -100 log.csv | awk 'BEGIN {print ",,,,"} {print}' | egrep ',$' | tail -1 | python corealarm.py "${args[@]:-${default_values[@]}}"
    sleep 20
done
