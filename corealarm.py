import sys
import time
import chime
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

america_new_york=ZoneInfo('America/New_York')

def make_a_racket():
    for theme in chime.themes():
        chime.theme(theme)
        chime.success()
        chime.warning()
        chime.error()
        chime.info()

def get_datetime(epoch_ns):
    seconds, nanoseconds = divmod(epoch_ns, 1_000_000_000)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    dt = dt.replace(microsecond=nanoseconds//1000)  # Convert nanoseconds to microseconds
    dt = dt.astimezone(america_new_york)
    return dt

def info(msg):
    dt=get_datetime(time.time_ns())
    print(dt,msg)
    sys.exit(-1)

def alarm(msg):
    dt=get_datetime(time.time_ns())
    print(dt,msg)
    make_a_racket()
    sys.exit(-1)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        alarm(f'usage: {sys.argv[0]} core_low core_high skin_low skin_high # in fahrenheit')
    try:
        core_low = float(sys.argv[1])
        core_high = float(sys.argv[2])
        skin_low = float(sys.argv[3])
        skin_high = float(sys.argv[4])
        assert core_low < core_high
        assert skin_low < skin_high
        assert core_low >= 95
        assert core_high <= 105
        assert skin_low >= 32
        assert skin_high <= 105
    except:
        alarm(f'bad argument(s): {sys.argv[1]} {sys.argv[2]} {sys.argv[3]} {sys.argv[4]}')

    # caller has already ensured there will be a line
    line = sys.stdin.readline().rstrip()
    try:
        [timestamp_str,core_temp_str,core_quality_str,skin_temp_str,_]=line.split(',')
    except:
        alarm(f'bad input line >>{line}<<, alarming')

    # get timestamp as America/New_York
    try:
        dt=get_datetime(int(timestamp_str))
    except:
        alarm(f'bad timestamp component >>{timestamp_str}<<, alarming')

    # check that timestamp is not stale
    try:
        now=get_datetime(time.time_ns())
        diff=now-dt
        assert diff < timedelta(seconds=90)
    except:
        alarm(f'stale timestamp {dt} is {diff} old, alarming')

    # check quality
    qualities = ['Poor','Fair','Good','Excellent'] # exclude Invalid and N/A intentionally
    if core_quality_str not in qualities:
        alarm(f'bad core quality component >>{core_quality_str}<<, alarming')

    # get core temp
    try:
        core_temp=float(core_temp_str)
    except:
        alarm(f'bad core temp component >>{core_temp_str}<<, alarming')

    # get skin temp
    try:
        skin_temp=float(skin_temp_str)
    except:
        alarm(f'bad skin temp component >>{skin_temp_str}<<, alarming')

    # check whether core temp in range
    if core_temp < core_low:
        alarm(f'core temp {core_temp:.2f} is too cold (less than {core_low})')
    if core_temp > core_high:
        alarm(f'core temp {core_temp:.2f} is too warm (more than {core_high})')

    # check whether skin temp in range
    if skin_temp < skin_low:
        alarm(f'skin temp {skin_temp:.2f} is too cold (less than {skin_low})')
    if skin_temp > skin_high:
        alarm(f'skin temp {skin_temp:.2f} is too warm (more than {skin_high})')

    # all checks pass!
    info(f'core temp {core_temp:.2f} is ok, skin temp {skin_temp:.2f} is ok @ {dt}')
