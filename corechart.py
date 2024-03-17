
###
### Note: this still needs some work
###


import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import pandas as pd
import numpy as np
from utils import get_datetime
from zoneinfo import ZoneInfo

# Define high and low threshold values for each series
if len(sys.argv)!=5:
    y1_high, y1_low = 99, 97.5
    y2_high, y2_low = 97, 65
else:
    y1_high, y1_low = (float(sys.argv[2]), float(sys.argv[1]))
    y2_high, y2_low = (float(sys.argv[4]), float(sys.argv[3]))

seekpos = 0
try:
    f=open('log.csv','rb')
except:
    print("can't access log.csv")
    sys.exit(-1)

# Initialize figure and first subplot for the first series
fig, ax1 = plt.subplots()
ax1.tick_params(axis='x', rotation=45)
x_data, y1_data, y2_data = [], [], []
line1 = ax1.plot_date(x_data, y1_data, '-', label='Core Body Temp', color='green')[0]

# Create a second y-axis for the second series
ax2 = ax1.twinx()
line2 = ax2.plot_date(x_data, y2_data, '-', label='Skin Temp', color='orange')[0]

# Draw horizontal lines for thresholds
ax1.axhline(y=y1_high, color='green', linestyle='-', linewidth=3, label='Core Body Temp High')
ax1.axhline(y=y1_low, color='green', linestyle='-', linewidth=3, label='Core Body Temp Low')
ax2.axhline(y=y2_high, color='orange', linestyle='-', linewidth=3, label='Skin Temp High')
ax2.axhline(y=y2_low, color='orange', linestyle='-', linewidth=3, label='Skin Temp Low')

last_line_y1 = None
last_line_y2 = None

def update(frame):
    global seekpos, last_line_y1, last_line_y2
    f.seek(seekpos)
    content=f.read()
    #print(content)
    lines=content.splitlines()
    content_length=len(content)

    # handle partial line
    if content_length and content[-1]!=b'\n'[0]:
        content_length -= len(lines[-1])
        lines.pop()
    seekpos += content_length # prepare for next time
    if not len(lines):
        return line1, line2 #, last_point_y1, last_point_y2

    for line in lines:
        line=line.decode()
        #print(line)
        try:
            [timestamp_str,core_temp_str,core_quality_str,skin_temp_str,_]=line.split(',')
            dt=get_datetime(int(timestamp_str))

            if len(core_temp_str):
                core_temp=float(core_temp_str)
            else:
                core_temp=np.nan

            skin_temp=float(skin_temp_str)

            # Simulate new data
            x_new = pd.Timestamp(dt)
            y1_new = core_temp  # Assuming a different scale for demonstration
            y2_new = skin_temp

            # look at the last x value and if too far from x_new, insert series NaNs to break line
            if len(x_data) and x_new - x_data[-1] > pd.Timedelta(seconds=10):
                diff = x_new - x_data[-1]
                if diff > pd.Timedelta(seconds=10):
                    x_data.append(x_new - diff / 2)
                    y1_data.append(np.nan)
                    y2_data.append(np.nan)
    
            # Append new data
            x_data.append(x_new)
            y1_data.append(y1_new)
            y2_data.append(y2_new)
        except Exception as e:
            print(e)
            print(f'bad input line >>{line}<<, ignoring')
    
    while x_data and x_data[0] < x_new - pd.Timedelta(hours=4):
        x_data.pop(0)
        y1_data.pop(0)
        y2_data.pop(0)
   
    # Update data
    line1.set_data(x_data, y1_data)
    line2.set_data(x_data, y2_data)

    # Always attempt to remove the previous y1 line, if it exists
    if last_line_y1 is not None:
        last_line_y1.remove()
        last_line_y1 = None  # Reset the reference
    
    # Only add a new line if the latest y1 data is not NaN
    if y1_data and not np.isnan(y1_data[-1]):
        last_y1_value = y1_data[-1]
        # Add a new horizontal line for the last y1 value
        last_line_y1 = ax1.axhline(y=last_y1_value, color='green', linestyle='--', linewidth=1)
        
    # Always attempt to remove the previous y2 line, if it exists
    if last_line_y2 is not None:
        last_line_y2.remove()
        last_line_y2 = None  # Reset the reference
    
    # Only add a new line if the latest y2 data is not NaN
    if y2_data and not np.isnan(y2_data[-1]):
        last_y2_value = y2_data[-1]
        # Add a new horizontal line for the last y2 value
        last_line_y2 = ax2.axhline(y=last_y2_value, color='orange', linestyle='--', linewidth=1)

    # Update or remove the last point markers
    #if not np.isnan(y1_data[-1]):
    #    last_point_y1.set_data([x_data[-1]], [y1_data[-1]])
    #else:
    #    last_point_y1.set_data([], [])  # Remove the X if the last y1_data is NaN

    #if not np.isnan(y2_data[-1]):
    #    last_point_y2.set_data([x_data[-1]], [y2_data[-1]])
    #else:
    #    last_point_y2.set_data([], [])  # Remove the X if the last y2_data is NaN

    ax1.set_xlim(x_data[-1] - pd.Timedelta(hours=4), x_data[-1])

    y1_data_range = [y for y in y1_data if y is not None and not np.isnan(y)]  # Exclude None or NaN
    y2_data_range = [y for y in y2_data if y is not None and not np.isnan(y)]  # Exclude None or NaN

    y1_min, y1_max = (min(y1_data_range)*.999, max(y1_data_range)*1.001)
    ax1.set_ylim([y1_min, y1_max])

    y2_min, y2_max = (min(y2_data_range)*.999, max(y2_data_range)*1.001)
    ax2.set_ylim([y2_min, y2_max])
    
    ax1.autoscale_view()
    ax2.autoscale_view()

    
    ax1.figure.canvas.draw()

    
    return line1, line2 #, last_point_y1, last_point_y2

# Set labels for both y-axes
ax1.set_ylabel('Core Body Temp', color='green')
ax2.set_ylabel('Skin Temp', color='orange')

date_formatter = mdates.DateFormatter('%H:%M', tz=ZoneInfo('America/New_York'))
ax1.xaxis.set_major_formatter(date_formatter)

ax1.yaxis.tick_right()
ax1.yaxis.set_label_position('right')
ax1.tick_params(axis='y', direction='in', labelcolor='green')
ax2.tick_params(axis='y', direction='in', labelcolor='orange')
ax2.spines['right'].set_position(('outward', 60))

# Create animation
ani = FuncAnimation(fig, update, cache_frame_data=False, interval=1000)  # Update every second

plt.tight_layout()  # Adjust layout to make room for the rotated x-axis labels
plt.show()

