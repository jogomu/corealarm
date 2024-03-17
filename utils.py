from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

america_new_york=ZoneInfo('America/New_York')

def get_datetime(epoch_ns):
    seconds, nanoseconds = divmod(epoch_ns, 1_000_000_000)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    dt = dt.replace(microsecond=nanoseconds//1000)  # Convert nanoseconds to microseconds
    dt = dt.astimezone(america_new_york)
    return dt

