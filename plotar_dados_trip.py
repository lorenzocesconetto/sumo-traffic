import os
import subprocess
import xml.etree.ElementTree as ET
from typing import List
import matplotlib.pyplot as plot
import sys


def gen_complete_name(file_name, period, i):
   period = str(period)

   # Make default name
   return file_name + '-' + str(period) + '-' + str(i) + '-trip'


def create_dir(file_name):
    # Creates plot_trip dir if it doesnt exist
    if not os.path.isdir(file_name + '/plot_trip'):
        subprocess.run(['mkdir', file_name + '/' + 'plot_trip'])


def get_data_single(file_name, period, opt='depart', is_sorted=True, file_number=0):
    period = float(period)
    data: List[int] = []

    # Make sure file exists
    name = file_name + '/out_trip/' + gen_complete_name(file_name, period, i=file_number) + '.out.xml'
    if not os.path.isfile(name):
        print('File not found: ' + name)
        sys.exit(1)

    # Open xml file
    root = ET.parse(name).getroot()
    for child in root:
        data.append(int(float(child.get(opt))))

    # Sort data
    if is_sorted:
        data.sort()

    return data


def get_data(file_name, opt='depart', period=1, number=1, is_sorted=True):
    data = []
    # Get data
    for i in range(number):
        tmp = []
        name = file_name + '/out_trip/' + gen_complete_name(file_name, period, i) + '.out.xml'
        if not os.path.isfile(name):
            print("Skipped file: " + name)
            continue
        root = ET.parse(name).getroot()
        for child in root:
            tmp.append(int(child.get(opt)))

        # Sort data
        if is_sorted:
            tmp.sort()

        # Append to final list
        data.append(tmp)

    # Make sure data is at least 3 sets of data no empty
    if len(data) < 3:
        print("Not graphing for period:", period, ' Because there are less than 3 samples')
        return None

    # Return list of lists of data
    return data


def p_function(t, insertion_times, max_time, step=1, n=2):
    n = int(n)
    step = int(step)
    num_insertions = insertion_times.count(t)
    # Check t
    if t < 0 or t > max_time:
        print("invalid t value")
        sys.exit(1)

    first = second = t
    j = 0
    # Find point under t
    while True:
        first -= step
        if first <= 0:
            first = 0
            num_insertions += insertion_times.count(0)
            break
        if first in insertion_times:
            num_insertions += insertion_times.count(first)
            j += 1
        if j >= n:
            break

    # Find point bellow t
    j = 0
    while True:
        second += step
        if second >= max_time:
            second = max_time
            break
        if second in insertion_times:
            num_insertions += insertion_times.count(second)
            j += 1
        if j >= n:
            num_insertions -= insertion_times.count(second)
            break

    return (second - first)/num_insertions


def get_avg(data, size):
    number = len(data)
    #   Make a vector with average values
    average = [0] * size
    for i in range(size):
        for j in data:
            average[i] += j[i] / number
    return average


def plot_data(x, y, file_name, period, file_number, n):
    # Create and format plot
    plot.plot(x, y)
    font_title = {'family': 'sans-serif',
                  'fontname': 'Verdana',
                  'color': 'darkred',
                  'weight': 'bold',
                  'size': 16,
                  }
    plot.title(file_name + ' ' + '(period=' + str(period) + ', n=' + str(n) + ')', fontdict=font_title)
    font_label = {'family': 'sans-serif',
                  'fontname': 'Arial',
                  'color': 'black',
                  'weight': 'normal',
                  'size': 12,
                  }
    plot.xlabel('Time (s)', fontdict=font_label)
    plot.ylabel('Actual Period (s/veh)', fontdict=font_label)
    plot.grid()
    # plot.ylim(ymin=-0.1, ymax=1)
    plot.savefig(file_name + '/plot_trip/' + file_name + '-' + str(period) + '-' + 'period' + '-' + str(file_number) + '-n='+ str(n) + '.png')
    plot.close()


def main(file_name, period=1, file_number=0, n=10):
    period = float(period)
    n = int(n)

    # Create dir ploT_trip
    create_dir(file_name)

    # Get list of lists of insertion times
    insertion_times = get_data_single(file_name, opt='depart', period=period, is_sorted=True, file_number=file_number)
    max_time = max(insertion_times)

    print(insertion_times)
    print(max_time)

    # Set up both axes
    # Get p value for each time
    y = [p_function(t=time, insertion_times=insertion_times, step=1, max_time=max_time, n=n) for time in range(max_time)]
    x = [t for t in range(max_time)]

    # Plot the data
    plot_data(x, y, file_name, period, file_number, n)


if __name__ == '__main__':
    main(file_name='new_manhattan', period=1, file_number=0, n=50)
    # print(get_data_single(file_name='new_manhattan', opt='depart', period=1, is_sorted=True, file_number=0))


