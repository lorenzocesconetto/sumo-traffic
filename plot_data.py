import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import matplotlib.pyplot as p
import argparse


def get_data(file_name, opt, period, number):
    data = []
    for i in range(number):
        tmp = []
        name = file_name + '/out/' + file_name + '-' + str(period)+ '-' + str(i) + '.out.xml'
        if not os.path.isfile(name):
            print("Skipped file: " + name)
            continue
        root = ET.parse(name).getroot()
        for child in root:
            tmp.append(float(child.get(opt)))
        data.append(tmp)
    if not data:
        print("Not graphing for period:", period)
    return data


def get_num_points(data):
    size = len(data[0])
    for i in data:
        if len(i) < size:
            size = len(i)
    return size


def get_max_min(data):
    #   Get minimun number of tuples
    size = get_num_points(data)
    #   Make min and max vectors
    max_vector = []
    min_vector = []
    for i in range(size):
        tmp_min = tmp_max = data[0][i]
        for j in data:
            if tmp_min > j[i]:
                tmp_min = j[i]
            if tmp_max < j[i]:
                tmp_max = j[i]
        max_vector.append(tmp_max)
        min_vector.append(tmp_min)
    return (max_vector, min_vector)


def get_avg(number, data):
    #   Get minimun number of tuples
    size = get_num_points(data)
    #   Make a vector with average values
    average = [0] * size
    for i in range(size):
        for j in data:
            average[i] += j[i] / number
    return average


def checks(file_name, opt1, opt2, period, number, options_dict):
    # Check if opt1 and opt2 provided are valid
    if opt1 not in options_dict or opt2 not in options_dict:
        print("\nBad usage.\npy plot.py op1 op2 file\nop1 and op2 might be:")
        print(', '.join(options_dict.keys()))
        sys.exit(1)

    # Check for a valid range
    if number > 10 or number <= 0 or period < 0.3:
        print("number must be a positive no bigger than 10\nPeriod must be larger than 0.3")
        sys.exit(1)

    # Check if dir exists
    if not os.path.isdir(file_name):
        print(f"Couldn't find directory named: {file_name}")
        sys.exit(1)

    # If plot dir doesn't exist, make it.
    if not os.path.isdir(file_name + '/' + 'plot'):
        subprocess.run(['mkdir', file_name + '/' + 'plot'])


def plot_data(file_name, period=1, number=10, opt1='time', opt2='meanWaitingTime'):
    options_dict = {"time": "Time (s)", "loaded": "Total number of cars loaded (#)",
                    "inserted": "Total number of cars inserted in the map (#)",
                    "running": "Number of cars currently in the map (#)",
                    "waiting": "Number of cars currently waiting at intersections (#)",
                    "ended": "Total number of cars that left the map (#)",
                    "meanWaitingTime": "Mean Waiting Time (s)", "meanTravelTime": "Mean Travel Time (s)",
                    "duration": "Duration (?)"}
    checks(file_name, opt1, opt2, period, number, options_dict)
    period = float(period)
    # Get data
    data_opt1 = get_data(file_name, opt1, period, number)
    data_opt2 = get_data(file_name, opt2, period, number)
    # Make sure lists are not empty
    if not data_opt1 or not data_opt2:
        return 0
    # Get average values
    x = get_avg(number, data_opt1)
    y = get_avg(number, data_opt2)

    # Create and format plot
    p.plot(x, y)
    font_title = {'family': 'sans-serif',
                  'fontname': 'Verdana',
                  'color': 'darkred',
                  'weight': 'bold',
                  'size': 16,
                  }
    p.title(file_name + ' ' + '(period=' + str(period) + ')', fontdict=font_title)
    font_label = {'family': 'sans-serif',
                  'fontname': 'Arial',
                  'color': 'black',
                  'weight': 'normal',
                  'size': 12,
                  }
    p.xlabel(options_dict[opt1], fontdict=font_label)
    p.ylabel(options_dict[opt2], fontdict=font_label)
    p.grid()
    # p.ylim(ymin=-0.1, ymax=1)
    max_vector, min_vector = get_max_min(data_opt2)
    p.fill_between(x, max_vector, min_vector, facecolor='orange', alpha=0.2, interpolate=True)
    p.savefig(file_name + '/' + 'plot' + '/' + file_name + '-' + str(period) + '-' + opt2 + '.png')
    # p.show()
    p.close()


if __name__ == "__main__":
    # plot_data(file_name, period='1', number='10', opt1='time', opt2='meanWaitingTime')
    parser = argparse.ArgumentParser()

    parser.add_argument("file_name", help="Folder name", type=str)
    parser.add_argument("-p", "--period", help="Period value", type=float, default=1)
    parser.add_argument("-n", "--number", help="Number of random files of input to graph", type=int, default=10)
    parser.add_argument("-x", "--opt1", help="X axis variable", type=str, default='time')
    parser.add_argument("-y", "--opt2", help="Y axis variable", type=str, default='meanWaitingTime')

    args = parser.parse_args()

    plot_data(**vars(args))





