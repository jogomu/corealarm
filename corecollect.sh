#!/bin/bash

while true; do
    python corecollect.py | tee -a log.csv
    sleep 1
done
