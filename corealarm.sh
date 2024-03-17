#!/bin/bash

while true; do
    # ensure we have at least one line to pass to corealarm.py
    tail -100 log.csv | awk 'BEGIN {print ",,,,"} {print}' | egrep ',$' | tail -1 | python corealarm.py "$@"
    sleep 20
done
