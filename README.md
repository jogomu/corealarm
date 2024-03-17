# corealarm

connect to CORE body temp sensor via BLE and alarm if outside target range for core and skin temps

run `corecollect.sh` and `corealarm.sh` in the same directory (shared access to log.csv)

optionally, run `python corechart.py` for a live-updating chart of the last 4 hours

these scripts will keep running corecollect.py and corealarm.py, respectively

currently not tested on Windows where you'd need bash+utils, also chart needs some work
