import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plot


####################
# Changeable
####################

# Directory for PLOT and simulations
OUT_DIR = 'out'
PLOT_DIR = 'plot'

# Directories for SIMULATIONS only
ROUTE_DIR = 'route'
CFG_DIR = 'cfg'

# Simulation
X_OPTION = 'time'
Y_OPTION = 'meanWaitingTime'
OUTPUT = 'summary-output'
STEP = 1
NUMBER_OF_SIMULATIONS = 10
DIRECTORIES = ['cfg', 'out', 'plot']
FILL_MAX_MIN = True
ROUTE_GENERATION_OPTIONS = {
                            # 'max-distance': 300,
                            'min-distance': 200,
                            'start': 0,
                            'end': 5400,
                            'fringe-factor': 10,
                            # 'speed-exponent': 10
                            }


####################
# Constants
####################
RANDOM_TRIPS_SCRIPT_PATH = '/Users/lorenzocesconetto/Applications/sumo-0.31.0/tools/randomTrips.py'
WORKING_DIRECTORY = '/Users/lorenzocesconetto/PyCharmProjects/sumo-tfc/src/'
BASE_CFG = 'base.sumo.cfg'
OUTPUT_OPTIONS = ["summary-output", "tripinfo-output"]
PLOT_AXIS_LABEL_OPTIONS = {"time": "Time (s)",
                           "loaded": "Total number of cars loaded (#)",
                           "inserted": "Total number of cars inserted in the map (#)",
                           "running": "Number of cars currently in the map (#)",
                           "waiting": "Number of cars currently waiting at intersections (#)",
                           "ended": "Total number of cars that left the map (#)",
                           "meanWaitingTime": "Mean Waiting Time (s)",
                           "meanTravelTime": "Mean Travel Time (s)",
                           "duration": "Duration (?)",
                           "depart": "Actual Period (s/veh)"}


####################
# Helpers
####################
def prefix_dash(text: str):
    if text and text[0] != '-':
        return '-' + text
    else:
        return text


def remove_prefix_dash(text: str):
    if text and text[0] == '-':
        return text[1:]
    else:
        return text


def format_attribute(attribute: str):
    return '--' + attribute + '='


def add_attribute(command_list: list, attribute: str, default: str = ''):
    if attribute in ROUTE_GENERATION_OPTIONS:
        command_list.append(format_attribute(attribute) + str(ROUTE_GENERATION_OPTIONS[attribute]))
    elif default:
        command_list.append(format_attribute(attribute) + str(default))


def generate_complete_name_with_index(file_name: str, period: float, i: int):
    """Returns a string in the format file_name-period-i-text"""
    return '-'.join([file_name, str(float(period)), str(i)])


def generate_complete_name(file_name: str, period: float):
    """Returns a string in the format file_name-period-i-text"""
    return '-'.join([file_name, str(float(period))])


####################
# Actions
####################
def set_working_directory(file_name: str=''):
    """Changes working directory into the network directory"""

    new_directory = WORKING_DIRECTORY + file_name

    if os.path.isdir(new_directory):
        os.chdir(new_directory)
    else:
        print('Directory not found: ' + WORKING_DIRECTORY + file_name)


def create_default_dirs(file_name: str):
    """Creates default directories in the file_name directory"""
    if not os.path.isdir(file_name):
        print('Directory not found: ' + os.getcwd() + '/' + file_name)
        sys.exit(1)

    dirs = [ROUTE_DIR, OUT_DIR, PLOT_DIR, CFG_DIR]
    absolute_path_dirs = [WORKING_DIRECTORY + file_name + '/' + x for x in dirs]

    for directory in absolute_path_dirs:
        if not os.path.isdir(directory):
            subprocess.run(['mkdir', directory])


def create_and_set_cfg_file(file_name: str, period: float):
    """
    Creates the configuration files in the directory file_name/cfg-text
    The file derives from the base_cfg parameter, which is set to base.sumo.cfg
    It always sets the route file to the route directory, never route-text
    """

    # Check if configuration file exists
    if not os.path.isfile(BASE_CFG):
        print('XML not found: ' + os.getcwd() + '/' + BASE_CFG)

    # Make sure network file exists
    network = file_name + '.net.xml'
    if not os.path.isfile(file_name + '/' + network):
        print('Network not found: ' + network)
        sys.exit(1)

    for i in range(NUMBER_OF_SIMULATIONS):
        # Make sure all route files exists
        route_file_name = generate_complete_name_with_index(file_name, period, i)
        route_file_path = '/'.join([file_name, ROUTE_DIR, route_file_name]) + '.rou.xml'
        if not os.path.isfile(route_file_path):
            print('Route file not found: ' + route_file_path)
            sys.exit(1)

        # Open XML in memory
        base = ET.parse(BASE_CFG)

        # Set network input
        base.find('input/net-file').set('value', '../' + network)

        # Set route input
        base.find('input/route-files').set('value', '../' + ROUTE_DIR + '/' + route_file_name + '.rou.xml')

        # Set output file to hold results
        output = base.find('output')
        # OUTPUT_TYPE could be 'summary-output' , 'tripinfo-output'
        ET.SubElement(output, OUTPUT, {'value': '../' + OUT_DIR + '/' + route_file_name + '.out.xml'})

        # Save configuration xml to file
        base.write(file_name + '/' + CFG_DIR + '/' + route_file_name + '.sumo.cfg')


def check_simulation_environment(file_name: str, period: float):
    """
    Checks if environment is setup to run
    Checks the existance of: default directories, network file,
    period and number are in a valid range, output_type is valid
    """

    # Check if file_name dir exists
    if not os.path.isdir(file_name):
        print(f"Couldn't find directory named: {file_name}")
        sys.exit(1)

    # Check if the .net.xml file exists
    if not os.path.isfile(file_name + '/' + file_name + '.net.xml'):
        print("Couldn't find network file: " + '/'.join([file_name, file_name]) + '.net.xml')
        sys.exit(1)

    # Check if NUMBER is valid
    if NUMBER_OF_SIMULATIONS <= 0 or NUMBER_OF_SIMULATIONS > 10:
        print("number must be a positive integer no larger than 10")
        sys.exit(1)

    # Check period value
    if period > 10 or period < 0.3:
        print("period must be a number between 0.3 and 10")
        sys.exit(1)

    # Check output type exists
    if OUTPUT not in OUTPUT_OPTIONS:
        print('OUTPUT_TYPE is not valid.\n' +
              'You entered: ' + OUTPUT + '\n' +
              'Options are: ' + str(OUTPUT_OPTIONS))
        sys.exit(1)


def generate_random_route_files(file_name: str, period: float):
    """
    Generates random trips and saves it into a routes file.
    The parameters taken into consideration are in the global
    dictionary variable RANDOM_TRIPS_SCRIPT_PATH
    """
    # Set up the possible attributes
    max_distance = 'max-distance'
    min_distance = 'min-distance'
    fringe_factor = 'fringe-factor'
    speed_exponent = 'speed-exponent'
    begin = 'begin'
    end = 'end'


    # Setup randomTrips.py command line
    command = []
    command.append(RANDOM_TRIPS_SCRIPT_PATH)
    command.append('-n')
    command.append(file_name + '/' + file_name + '.net.xml')

    # Add the attributes passed to the ROUTE_GENERATION_OPTIONS dictionary
    add_attribute(command, max_distance)
    add_attribute(command, min_distance)
    add_attribute(command, fringe_factor)
    add_attribute(command, speed_exponent)
    add_attribute(command, begin, '0')
    add_attribute(command, end, '1000')

    command.append('--period=' + str(period))
    command.append('-r')

    # Add the final element to command list, which is the output route file
    for i in range(NUMBER_OF_SIMULATIONS):
        # Append path for route file
        complete_name = generate_complete_name_with_index(file_name, period, i)
        complete_name_with_path = '/'.join([file_name, ROUTE_DIR, complete_name])
        command.append(complete_name_with_path + '.rou.xml')

        # Create route file
        subprocess.run(command)

        # Remove path to output route file
        command.pop()

        # Remove trash files generated by command
        file_to_be_removed = complete_name_with_path + '.rou.alt.xml'
        subprocess.run(['rm', 'trips.trips.xml', file_to_be_removed])


def run_simulations(file_name: str, period: float):
    """
    Runs simulation for that file_name for a period and number files.
    Saves to cfg-text directory
    """
    for i in range(NUMBER_OF_SIMULATIONS):
        complete_name = generate_complete_name_with_index(file_name, period, i)
        subprocess.run(['sumo', '-c', '/'.join([file_name, CFG_DIR, complete_name + '.sumo.cfg'])])


def get_single_data_from_output(file_name: str, period: float, opt: str,
                                sorted_output: bool=True, file_number: int=0,
                                integer_output: bool=True):
    """
    Get data from a single out.xml file and return it into a list.
    parameter opt could be: depart, departDelay, meanWaitingTime, etc.
    If integer_output is set to false, it will return float output.
    """
    data = []

    # Make sure file exists
    name = file_name + '/' + OUT_DIR + '/' + generate_complete_name_with_index(file_name, period, file_number) + '.out.xml'
    if not os.path.isfile(name):
        print('File not found: ' + name)
        sys.exit(1)

    # Open xml file
    root = ET.parse(name).getroot()
    if integer_output:
        for child in root:
            data.append(int(float(child.get(opt))))
    else:
        for child in root:
            data.append(float(child.get(opt)))

    # Sort data
    if sorted_output:
        data.sort()

    return data


def get_data_from_all_simulations_output(file_name: str, opt: str, period: float):
    """
    Get data from a all out.xml file and return it into a list of lists.
    Each list is holds the opt values for one specific simulation.
    parameter opt could be: depart, departDelay, meanWaitingTime, etc.
    If integer_output is set to false, it will return float output.
    [[x_1, x_2, ...], [x_1, x_2...], ...]
    """
    data = []

    # Iterate through each simulation output file
    for i in range(NUMBER_OF_SIMULATIONS):
        tmp = []
        name = file_name + '/' + OUT_DIR + '/' + generate_complete_name_with_index(file_name, period, i) + '.out.xml'

        # Skip file not found
        if not os.path.isfile(name):
            print("Skipped file: " + name)
            continue

        # Get xml root and iterate to obtain data
        root = ET.parse(name).getroot()
        for child in root:
            tmp.append(float(child.get(opt)))

        # Append to final list
        data.append(tmp)

    # Return list of lists of data
    return data


def get_insertion_rate_at_point(time_point, insertion_times, step=1, offset=2):
    """Returns the average period of insertion of offset number of points"""

    offset = int(offset)
    step = int(step)
    num_insertions = insertion_times.count(time_point)

    # Check t
    max_time = max(insertion_times)
    if time_point < 0 or time_point > max_time:
        print("invalid time_point value")
        sys.exit(1)

    # Define variables
    first = second = time_point
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


def get_average_from_list_of_lists(data: list):
    """Averages each corresponding elements of a list of lists"""
    # Get shortest list length
    size_of_output_vector = get_size_of_smallest_list(data)

    # Get number of lists inside data
    number_of_elements = len(data)

    # Create vector to receive the average values
    average = [0] * size_of_output_vector

    # Iterate through
    for i in range(size_of_output_vector):
        for d in data:
            average[i] += d[i] / number_of_elements
    return average


def get_size_of_smallest_list(data: list):
    """Gets the smallest length of all lists inside the data list of lists"""
    size = len(data[0])
    for d in data:
        if len(d) < size:
            size = len(d)
    return size


def get_max_min_vectors_from_list_of_lists(data: list):
    """
    Gets the minimum and the maximum values of the
    corresponding elements in a list of lists.
    returns a dictionary with two lists as
    {'maximum': [max_i, max_i+1, ...], 'minimum': [min_i, min_i+1, ...]}
    """
    # Get length of shortest list
    size_of_output_vector = get_size_of_smallest_list(data)

    #   Make min and max vectors
    maximum_vector = [0] * size_of_output_vector
    minimum_vector = [0] * size_of_output_vector
    for i in range(size_of_output_vector):
        temporary_minimum = temporary_maximum = data[0][i]
        for d in data:
            if temporary_minimum > d[i]:
                temporary_minimum = d[i]
            if temporary_maximum < d[i]:
                temporary_maximum = d[i]
        maximum_vector[i] = temporary_maximum
        minimum_vector[i] = temporary_minimum
    return {'maximum': maximum_vector, 'minimum': minimum_vector}


def check_plotting_environment(file_name: str, x_label_option: str, y_label_option: str):
    """Checks if all proper directories and files exist to create a plot"""

    # Check if x_opt provided is valid
    if x_label_option not in PLOT_AXIS_LABEL_OPTIONS:
        print("Could not find x_opt,\nopt might be:")
        print(', '.join(PLOT_AXIS_LABEL_OPTIONS.keys()))
        sys.exit(1)

    # Check if opt2 provided is valid
    if y_label_option not in PLOT_AXIS_LABEL_OPTIONS:
        print("Could not find y_opt,\nopt might be:")
        print(', '.join(PLOT_AXIS_LABEL_OPTIONS.keys()))
        sys.exit(1)

    # Check if dir exists
    if not os.path.isdir(file_name):
        print(f"Couldn't find directory named: {file_name}")
        sys.exit(1)

    plot_directory = file_name + '/' + PLOT_DIR
    if not os.path.isdir(plot_directory):
        subprocess.run(['mkdir', plot_directory])


def plot_data(x_axis_data: list, y_axis_data: list, x_label_option: str, y_label_option: str,
              file_name: str, period: float, fill_max_min: bool,
              maximums_vector: list, minimums_vector: list):
    """Plot the data"""
    # Check directories exist and numbers are within acceptable range
    check_plotting_environment(file_name=file_name, x_label_option=x_label_option,
                               y_label_option=y_label_option)

    # Create and format plot
    plot.plot(x_axis_data, y_axis_data)

    # Title format
    title_font_style = {'family': 'sans-serif',
                        'fontname': 'Verdana',
                        'color': 'darkred',
                        'weight': 'bold',
                        'size': 16}

    # Title text
    plot.title(file_name + ' ' + '(period=' + str(float(period)) + ')', fontdict=title_font_style)

    # Label format
    label_font_style = {'family': 'sans-serif',
                        'fontname': 'Arial',
                        'color': 'black',
                        'weight': 'normal',
                        'size': 12}

    # Label text
    plot.xlabel(PLOT_AXIS_LABEL_OPTIONS[x_label_option], fontdict=label_font_style)
    plot.ylabel(PLOT_AXIS_LABEL_OPTIONS[y_label_option], fontdict=label_font_style)

    # Add grid lines
    plot.grid()

    # Fill maximum and minimum range of the data
    if fill_max_min:
        if not maximums_vector or not minimums_vector:
            print("Must provide max_vector and min_vector.")
            sys.exit(1)
        plot.fill_between(x_axis_data, maximums_vector, minimums_vector,
                          facecolor='orange', alpha=0.2, interpolate=True)

    # Saving name
    plot.savefig(file_name + '/' + PLOT_DIR + '/' +
                 generate_complete_name(file_name=file_name, period=period)
                 + '.png')

    # Close file and free from memory
    plot.close()


# Review needed
def plot_data_with_offset(x_axis_data: list, y_axis_data: list, x_label_option: str, y_label_option: str,
                          file_name: str, period: float, file_number: int, offset: int):
    """Plot the data"""
    # Check directories exist and numbers are within acceptable range
    check_plotting_environment(file_name=file_name, x_label_option=x_label_option,
                               y_label_option=y_label_option)

    # Create and format plot
    plot.plot(x_axis_data, y_axis_data)

    # Title format
    font_title = {'family': 'sans-serif',
                  'fontname': 'Verdana',
                  'color': 'darkred',
                  'weight': 'bold',
                  'size': 16}

    # Title text
    plot.title(file_name + ' ' + '(period=' + str(period) + ', offset=' + str(offset) + ')',
               fontdict=font_title)

    # Label format
    font_label = {'family': 'sans-serif',
                  'fontname': 'Arial',
                  'color': 'black',
                  'weight': 'normal',
                  'size': 12}

    # Label text
    plot.xlabel(PLOT_AXIS_LABEL_OPTIONS[x_label_option], fontdict=font_label)
    plot.ylabel(PLOT_AXIS_LABEL_OPTIONS[y_label_option], fontdict=font_label)

    # Add grid lines
    plot.grid()

    # Saving file with a given name
    plot.savefig(file_name + '/' + PLOT_DIR + '/'
                 + generate_complete_name_with_index(file_name=file_name, period=period, i=file_number)
                 + '-period-offset=' + str(offset) + '.png')

    # Close file and free from memory
    plot.close()


####################
# Performs entire tasks
####################
def script_run_plot(file_name: str, period: float):
    """
    Gather the data from the output, and print it.
    Does not run or setup any simulations.
    """
    # Set working dir to src
    set_working_directory()

    # Get y data
    y_full_data = get_data_from_all_simulations_output(file_name, Y_OPTION, period)
    y_data = get_average_from_list_of_lists(y_full_data)

    # Get x data
    x_data = [x for x in range(get_size_of_smallest_list(y_full_data))]

    # Get max and min vectors
    max_min_dictionary = get_max_min_vectors_from_list_of_lists(y_full_data)
    maximums_vector = max_min_dictionary['maximum']
    minimums_vector = max_min_dictionary['minimum']

    # Plot data
    plot_data(x_data, y_data, X_OPTION, Y_OPTION, file_name, period,
              FILL_MAX_MIN, maximums_vector, minimums_vector)


def script_run_simulations(file_name: str, period: float):
    """
    Runs all simulations and generates results.
    After that, it also plots the results.
    """
    set_working_directory()

    # Checks the environment
    check_simulation_environment(file_name, period)

    # Creates default directories
    create_default_dirs(file_name)

    # Generates rou.xml files
    generate_random_route_files(file_name, period)

    # Creates sumo.cfg files
    create_and_set_cfg_file(file_name, period)

    # Run simulation
    run_simulations(file_name, period)


def script_run_complete(file_name: str, period: float):
    script_run_simulations(file_name, period)
    script_run_plot(file_name, period)







