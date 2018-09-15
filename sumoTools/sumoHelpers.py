import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plot


def gen_complete_name(file_name, period, i, text=''):
    """Returns a string in the format file_name-period-i-text"""

    if text and text[0] == '-':
        text = text[1:]
    if i == -1:
        return '-'.join([file_name, str(period), text])
    else:
        return '-'.join([file_name, str(period), str(i), text])


def create_dirs(file_name, *args, text=''):
    """Creates directories in the file_name directory"""

    if not os.path.isdir(file_name):
        print('Directory not found: ' + file_name)
        sys.exit(1)

    if text:
        dirs = ['-'.join([x, text]) for x in args]
    else:
        dirs = [*args]

    abs_dirs = [file_name + '/' + x for x in dirs]

    for directory in abs_dirs:
        if not os.path.isdir(directory):
            subprocess.run(['mkdir', directory])


def create_cfg(file_name, period, number, output_type, base_cfg='base.sumo.cfg', text=''):
    """Creates the configuration files in the directory file_name/cfg-text based on xml base_cfg"""

    # Check configuration file exists
    if not os.path.isfile(base_cfg):
        print('XML not found: ' + base_cfg)

    if text and text[0] != '-':
        text = '-' + text

    # Make sure network file exists
    network = file_name + '.net.xml'
    if not os.path.isfile(file_name + '/' + network):
        print('Network not found: ' + network)
        sys.exit(1)

    for i in range(number):

        # Make sure route exists
        name = gen_complete_name(file_name, period, i)
        if not os.path.isfile('/'.join([file_name, 'route', name]) + '.rou.xml'):
            print('Route file not found: ' + '/'.join([file_name, 'route', name]) + '.rou.xml')
            sys.exit(1)

        # Open XML in memory
        base = ET.parse(base_cfg)

        # Set network input
        base.find('input/net-file').set('value', '../' + network)

        # Set route input
        base.find('input/route-files').set('value', '../route/' + name + '.rou.xml')

        # Set output file to hold results
        output = base.find('output')
        # output_type could be 'summary-output' , 'tripinfo-output'
        ET.SubElement(output, output_type, {'value': '../out' + text + '/' + name + '.out.xml'})

        # Save configuration xml to file
        base.write(file_name + '/cfg' + text + '/' + name + '.sumo.cfg')


def checks_random_cfg(file_name, period, number, output_type):

    """Checks if exists: directories, the network file, period and number are in a valid range, output_type is valid"""
    # Check if file_name dir exists
    if not os.path.isdir(file_name):
        print(f"Couldn't find directory named: {file_name}")
        sys.exit(1)

    # Check if the .net.xml file exists
    if not os.path.isfile(file_name + '/' + file_name + '.net.xml'):
        print("Couldn't find network file: " + '/'.join([file_name, file_name]) + '.net.xml')
        sys.exit(1)

    # Check if n is valid
    if number <= 0 or number > 10:
        print("number must be positive and no larger than 10")
        sys.exit(1)

    # Check period value
    if period > 10 or period < 0.3:
        print("period must be between 0.3 and 10")
        sys.exit(1)

    # Check output type exists
    options = ["summary-output", "tripinfo-output"]
    if output_type not in options:
        print("output_type is not valid.\n You entered: " + output_type + "\nOptions are: " + str(options))
        sys.exit(1)


def gen_random_trips(file_name, period, number=10):
    # Setup randomTrips.py command line
    command = []
    command.append('/Users/lorenzocesconetto/Applications/sumo-0.31.0/tools/randomTrips.py')
    command.append('-n')
    command.append(file_name + '/' + file_name + '.net.xml')
    # command.append('--max-distance=300')
    # command.append('--min-distance=100')
    command.append('--fringe-factor=10')
    # command.append('--speed-exponent=2')
    command.append('--begin=0')
    command.append('--end=1000')
    command.append('--period=' + str(period))
    command.append('-r')

    for i in range(number):
        # Append path for route file
        comp_name = gen_complete_name(file_name, period, i)
        route_name = '/'.join([file_name + 'route' + comp_name]) + '.rou.xml'
        command.append(route_name)

        # Create route file
        subprocess.run(command)

        # Remove path route file
        command.pop()

        # Remove trash files
        del_name = '/'.join([file_name + 'route' + comp_name]) + '.rou.alt.xml'
        subprocess.run(['rm', 'trips.trips.xml', del_name])


def run_simulation(file_name, period, number, text=''):
    """Runs simulation for that file_name for a period and number files. Saves to cfg-text directory"""

    if text and text[0] != '-':
        text = '-' + text
    for i in range(number):
        comp_name = gen_complete_name(file_name, period, i)
        subprocess.run(['sumo', '-c', '/'.join([file_name, 'cfg' + text, comp_name + '.sumo.cfg'])])


def get_data_single(file_name, period, opt, sorted_output=True, file_number=0, integer_output=True, text=''):
    """Get data from a single out.xml file"""

    data = []

    # Add '-' to the
    if text and text[0] != '-':
        text = '-' + text

    # Make sure file exists
    name = file_name + '/out' + text + '/' + gen_complete_name(file_name, period, i=file_number) + '.out.xml'
    if not os.path.isfile(name):
        print('File not found: ' + name)
        sys.exit(1)

    # Open xml file
    root = ET.parse(name).getroot()
    for child in root:
        if integer_output:
            data.append(int(float(child.get(opt))))
        else:
            data.append(float(child.get(opt)))

    # Sort data
    if sorted_output:
        data.sort()

    return data


def get_data(file_name, opt, period, number, sorted_output=False, integer_output=True, text=''):
    data = []

    if text:
        text = '-' + text

    # Get data
    for i in range(number):
        tmp = []
        name = file_name + '/out' + text + '/' + gen_complete_name(file_name, period, i) + '.out.xml'

        # Skip file not found
        if not os.path.isfile(name):
            print("Skipped file: " + name)
            continue

        # Get xml root and iterate to obtain data
        root = ET.parse(name).getroot()
        if integer_output:
            for child in root:
                tmp.append(int(float(child.get(opt))))
        else:
            for child in root:
                tmp.append(float(child.get(opt)))

        # Sort data
        if sorted_output:
            tmp.sort()

        # Append to final list
        data.append(tmp)

    # Make sure data is at least 3 sets of data
    if len(data) < 3:
        print("Not graphing for period:", period, ' Because there are less than 3 samples')
        return None

    # Return list of lists of data
    return data


def p_function(t, insertion_times, step=1, offset=2):
    """Returns the average period of insertion of offset number of points"""

    offset = int(offset)
    step = int(step)
    num_insertions = insertion_times.count(t)

    # Check t
    max_time = max(insertion_times)
    if t < 0 or t > max_time:
        print("invalid t value")
        sys.exit(1)

    # Define variables
    first = second = t
    j = 0
    # Find point before t
    while True:
        first -= step
        if first <= 0:
            first = 0
            num_insertions += insertion_times.count(0)
            break
        if first in insertion_times:
            num_insertions += insertion_times.count(first)
            j += 1
        if j >= offset:
            break

    # Find point after t
    j = 0
    while True:
        second += step
        if second >= max_time:
            second = max_time
            break
        if second in insertion_times:
            num_insertions += insertion_times.count(second)
            j += 1
        if j >= offset:
            num_insertions -= insertion_times.count(second)
            break

    return (second - first) / num_insertions


def get_avg(data, size):
    """Averages each corresponding element of a list of lists"""

    number = len(data)
    #   Make a vector with average values
    average = [0] * size
    for i in range(size):
        for j in data:
            average[i] += j[i] / number
    return average


def get_num_points(data):
    """Gets the minimum number of points of all lists inside the data list of lists"""

    size = len(data[0])
    for i in data:
        if len(i) < size:
            size = len(i)
    return size


def get_max_min(data):
    """Gets the minimum and the maximum values of the corresponding elements in a list of lists and returns the values as a tuple"""

    #   Get minimum number of tuples
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
    return max_vector, min_vector


def check_plot(file_name, x_opt, y_opt, options_dict):
    """Checks if all directories and files exist to create a plot"""

    # Check if x_opt provided is valid
    if x_opt not in options_dict:
        print("Could not find x_opt,\nopt might be:")
        print(', '.join(options_dict.keys()))
        sys.exit(1)

    # Check if opt2 provided is valid
    if y_opt not in options_dict:
        print("Could not find y_opt,\nopt might be:")
        print(', '.join(options_dict.keys()))
        sys.exit(1)

    # Check if dir exists
    if not os.path.isdir(file_name):
        print(f"Couldn't find directory named: {file_name}")
        sys.exit(1)


def plot_data(x, y, x_opt, y_opt, file_name, period, file_number=-1, offset=0, text='', fill_max_min=False,
              max_vector=0, min_vector=0):
    """Plot the data"""

    options_dict = {"time": "Time (s)",
                    "loaded": "Total number of cars loaded (#)",
                    "inserted": "Total number of cars inserted in the map (#)",
                    "running": "Number of cars currently in the map (#)",
                    "waiting": "Number of cars currently waiting at intersections (#)",
                    "ended": "Total number of cars that left the map (#)",
                    "meanWaitingTime": "Mean Waiting Time (s)",
                    "meanTravelTime": "Mean Travel Time (s)",
                    "duration": "Duration (?)",
                    "depart": "Actual Period (s/veh)"}

    # Check directories exist and numbers are within acceptable range
    check_plot(file_name=file_name, x_opt=x_opt, y_opt=y_opt,
               options_dict=options_dict)

    # Add "-" to text
    if text:
        text = '-' + text

    # Create and format plot
    plot.plot(x, y)
    # Title format
    font_title = {'family': 'sans-serif',
                  'fontname': 'Verdana',
                  'color': 'darkred',
                  'weight': 'bold',
                  'size': 16}

    # If offset is provided or not
    # Title text
    if offset:
        plot.title(file_name + ' ' + '(period=' + str(period) + ', offset=' + str(offset) + ')', fontdict=font_title)
    else:
        plot.title(file_name + ' ' + '(period=' + str(period) + ')', fontdict=font_title)

    # Label format
    font_label = {'family': 'sans-serif',
                  'fontname': 'Arial',
                  'color': 'black',
                  'weight': 'normal',
                  'size': 12}

    # Label text
    plot.xlabel(options_dict[x_opt], fontdict=font_label)
    plot.ylabel(options_dict[y_opt], fontdict=font_label)

    # Add grid lines
    plot.grid()

    # Fill maximum and minimum range of the data
    if fill_max_min:
        if not max_vector or not min_vector:
            print("Must provide max_vector and min_vector.")
            sys.exit(1)
        plot.fill_between(x, max_vector, min_vector, facecolor='orange', alpha=0.2, interpolate=True)

    # Saving name
    if offset:
        plot.savefig(
            file_name + '/plot' + text + '/' + gen_complete_name(file_name=file_name, period=period, i=file_number,
                                                                 text=text) + '-period-offset=' + str(offset) + '.png')
    else:
        plot.savefig(file_name + '/plot' + text + '/' +
                     gen_complete_name(file_name=file_name, period=period, i=file_number)
                     + '-' + y_opt + '.png')

    # Close file and free from memory
    plot.close()




















