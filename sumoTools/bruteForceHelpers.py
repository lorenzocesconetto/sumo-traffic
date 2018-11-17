import sumoTools.simulationHelpers as SH
import sumoTools.Constants as Const
import sumoTools.bfConstants as bfConst
import sys
import os
import subprocess
import xml.etree.ElementTree
import matplotlib.pyplot


def read_tl_id(file_name: str):
    path_to_network_file = os.path.join(Const.WORKING_DIRECTORY, file_name, file_name + Const.NET_FILE_EXTENSION)
    base = xml.etree.ElementTree.parse(path_to_network_file)
    return base.find('tlLogic').attrib['id']


def read_tl_states(file_name: str):
    path_to_network_file = os.path.join(Const.WORKING_DIRECTORY, file_name, file_name + Const.NET_FILE_EXTENSION)
    base = xml.etree.ElementTree.parse(path_to_network_file)
    tlLogic_element = base.find('tlLogic')

    data = []
    for child in tlLogic_element:
        data.append(child.attrib['state'])

    if len(data) != bfConst.NUMBER_OF_PHASES:
        print('Number of phases read in the file: ' + path_to_network_file + '\n')
        print('doesn\'t match the input in the sumoTools/simulationConstants.py file.\n')

    return data


def make_tl_name(period: float):
    return Const.TL_FILE + '-' + str(period) + Const.TL_FILE_EXTENSION


def create_tl_dir(file_name: str):
    """
        Create a directory to take all the additional files
        to the traffic light.
    """
    SH.set_working_directory()

    for directory in [Const.TL_DIR, bfConst.OUT_DIR_TL, bfConst.CFG_DIR_TL, Const.PLOT_DIR]:
        if not os.path.isdir(os.path.join(file_name, directory)):
            subprocess.run(['mkdir', os.path.join(file_name, directory)])


def generate_possibilities():
    """
        Generate a list of tuples in the format [ (cycle_time, green_time, red_time), (...) ... ]
        which represents all possible programs.
        It also limits the red time so we can reduce the number of possibilities based
        on what we know
    """
    yellow_duration = bfConst.NUMBER_OF_YELLOW_PHASES * bfConst.YELLOW_DURATION

    # Check if numbers are valid
    if (
        (yellow_duration + bfConst.NUMBER_OF_RED_GREEN_PHASES * bfConst.MIN_PHASE_DURATION) > bfConst.MAX_CYCLE
            or (yellow_duration + bfConst.NUMBER_OF_RED_GREEN_PHASES * bfConst.MAX_PHASE_DURATION) < bfConst.MIN_CYCLE
            or bfConst.MIN_CYCLE > bfConst.MAX_CYCLE):
        print('Invalid cycle values. Please check numbers.\n')
        sys.exit(1)

    # Create list to be returned
    possibilities = []

    # Iterate possible values
    for cycle_time in range(bfConst.MIN_CYCLE, bfConst.MAX_CYCLE + 1):

        minimum_time = cycle_time - yellow_duration - bfConst.MAX_PHASE_DURATION * (bfConst.NUMBER_OF_RED_GREEN_PHASES - 1)
        maximum_time = cycle_time - yellow_duration - bfConst.MIN_PHASE_DURATION * (bfConst.NUMBER_OF_RED_GREEN_PHASES - 1)

        for green_time in range(
                max(bfConst.MIN_PHASE_DURATION, minimum_time),
                1 + min(bfConst.MAX_PHASE_DURATION, maximum_time)):

            red_time = cycle_time - green_time - yellow_duration

            if red_time <= bfConst.MAX_RED_TIME and green_time >= bfConst.MIN_GREEN_TIME:
                possibilities.append(
                    {'cycle_time': cycle_time, 'green_time': green_time, 'red_time': red_time})

    return possibilities


def create_tl_program_file(file_name: str, timing: list, states: list, period: float):
    """
        file_name: topology name
        timing: array of duration for each phase
        states: array of strings of each state
        i: Index of the TL program in the list of generate_possibilities()
        period: Period of the insertion of vehicles
        returns: null
        Only writes a file for traffic light configuration
    """
#<additional>
#   <tlLogic>
#       <tlLogic id="gneJ3" type="static" programID="0" offset="0">
#       <phase duration="41" state="GrrG"/>
#       <phase duration="4" state="yrry"/>
#       <phase duration="41" state="rGGr"/>
#       <phase duration="4" state="ryyr"/>
#   </tlLogic>
#<additional>

    SH.set_working_directory()

    file = open(os.path.join(file_name, Const.TL_DIR, make_tl_name(period=period)), 'w')
    file.write('<additional>\n')
    file.write('\t<tlLogic id="' + read_tl_id(file_name) + '" type="static" programID="my_program" offset="0">\n')
    for i in range(bfConst.NUMBER_OF_PHASES):
        file.write('\t\t<phase duration="' + str(timing[i]) + '" state="' + states[i] + '"/>\n')
    file.write('\t</tlLogic>\n')
    file.write('</additional>\n')


def create_cfg_and_add_tl_program(file_name: str, period: float):

    SH.set_working_directory()
    network_file = file_name + Const.NET_FILE_EXTENSION
    if not os.path.isfile(os.path.join(file_name, network_file)):
        print('Network not found: ' + network_file)
        sys.exit(1)

    for i in range(Const.NUMBER_OF_SIMULATIONS):
        name = SH.generate_complete_name_with_index(file_name, period, i)
        route_file_path = os.path.join(file_name, Const.ROUTE_DIR, name + Const.ROUTE_FILE_EXTENSION)

        if not os.path.isfile(route_file_path):
            print('Route file not found: ' + route_file_path)
            sys.exit(1)

        # Open XML in memory
        base = xml.etree.ElementTree.parse(Const.BASE_CFG)

        # Set network input
        base.find('input/net-file').set('value', '../' + network_file)

        # Set route input
        base.find('input/route-files').set('value', '../' + Const.ROUTE_DIR + '/' + name + Const.ROUTE_FILE_EXTENSION)

        # Set output file
        output = base.find('output')
        xml.etree.ElementTree.SubElement(output, Const.OUTPUT,
                      {'value': os.path.join('..', bfConst.OUT_DIR_TL,
                                             SH.generate_complete_name_with_index(file_name, period, i)
                                             + Const.OUT_FILE_EXTENSION)})

        # Add Traffic Light program
        cfg_file_buffer = base.find('input')
        xml.etree.ElementTree.SubElement(cfg_file_buffer, Const.ADDITIONAL_FILE_TAG,
                                         {'value': os.path.join('..', Const.TL_DIR,
                                                                make_tl_name(period=period))})

        # Save configuration xml to file
        base.write(os.path.join(file_name, bfConst.CFG_DIR_TL,
                                SH.generate_complete_name_with_index(file_name, period, i)
                                + Const.CFG_FILE_EXTENSION))


def run_simulation_tl(file_name: str, period: float):
    """
        Runs simulation for that file_name for a period and number files.
        Saves to cfg directory
    """
    for i in range(Const.NUMBER_OF_SIMULATIONS):
        complete_name = SH.generate_complete_name_with_index(file_name, period, i)
        subprocess.run(['sumo', '--no-warnings', '-c',
                        os.path.join(Const.WORKING_DIRECTORY, file_name,
                                     bfConst.CFG_DIR_TL, complete_name + Const.CFG_FILE_EXTENSION)])


def get_data(file_name: str, period: float, i: int, opt: str):
    """
        Get data from a single *.out.xml file and return it into a list.
        Parameter opt could be: depart, departDelay, meanWaitingTime, etc.
        Returns [x1, x2, ...]
    """
    name = os.path.join(file_name, bfConst.OUT_DIR_TL,
                        SH.generate_complete_name_with_index(file_name, period, i) + Const.OUT_FILE_EXTENSION)

    if not os.path.isfile(name):
        print('Could not find file: ' + name)
        sys.exit(1)

    data = []

    # Open xml file
    root = xml.etree.ElementTree.parse(name).getroot()

    for child in root:
        data.append(float(child.get(opt)))

    return data


def get_data_from_file_path(file_path: str, opt: str):
    data = []

    # Open xml file
    root = xml.etree.ElementTree.parse(file_path).getroot()

    for child in root:
        data.append(float(child.get(opt)))

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
    for i in range(Const.NUMBER_OF_SIMULATIONS):
        tmp = []
        name = os.path.join(Const.WORKING_DIRECTORY, file_name, bfConst.OUT_DIR_TL,
                            SH.generate_complete_name_with_index(file_name, period, i) + Const.OUT_FILE_EXTENSION)

        # Skip file not found
        if not os.path.isfile(name):
            print("Skipped file: " + name)
            continue

        # Get xml root and iterate to obtain data
        root = xml.etree.ElementTree.parse(name).getroot()
        for child in root:
            tmp.append(float(child.get(opt)))

        # Append to final list
        data.append(tmp)

    # Return list of lists of data
    return data


def measure_performance(data):
    """
        data: Considering data is a list of lists
        return: a float as the average of the last values
    """
    total_sum = 0

    for d in data:
        total_sum += max(d)

    return total_sum / len(data)


def delete_files(file_name: str, period: float):
    """
        Deletes output and cfg files.
        Doesn't return anything.
    """
    SH.set_working_directory()

    tl_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, Const.TL_DIR,
                                make_tl_name(period=period))
    if os.path.isfile(tl_file_path):
        os.remove(tl_file_path)
    else:
        print('File to be deleted not found: ' + tl_file_path + '\n')
        sys.exit(1)

    for i in range(Const.NUMBER_OF_SIMULATIONS):
        name = SH.generate_complete_name_with_index(file_name, period, i)

        out_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, bfConst.OUT_DIR_TL,
                                     name + Const.OUT_FILE_EXTENSION)

        cfg_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, bfConst.CFG_DIR_TL,
                                     name + Const.CFG_FILE_EXTENSION)

        files = [out_file_path, cfg_file_path]

        for file in files:
            if os.path.isfile(file):
                os.remove(file)
            else:
                print('File to be deleted not found: ' + file + '\n')
                sys.exit(1)


def execute_tl_attempt(file_name: str, period: float, timing: list, tl_states: list):
    create_tl_program_file(file_name=file_name, timing=timing, states=tl_states, period=period)
    create_cfg_and_add_tl_program(file_name=file_name, period=period)
    run_simulation_tl(file_name=file_name, period=period)


def pick_the_best_tl_program(file_name: str, period: float):
    period = float(period)
    SH.set_working_directory()
    create_tl_dir(file_name)
    possibilities = generate_possibilities()
    tl_states = read_tl_states(file_name=file_name)

    buffer = None
    for i in range(len(possibilities)):
        timing = [possibilities[i]['green_time'],
                  bfConst.YELLOW_DURATION,
                  possibilities[i]['red_time'],
                  bfConst.YELLOW_DURATION]

        execute_tl_attempt(file_name=file_name, period=period, timing=timing, tl_states=tl_states)
        data = get_data_from_all_simulations_output(file_name=file_name,
                                                    opt=Const.Y_OPTION, period=period)
        performance = measure_performance(data)
        if buffer is None:
            buffer = {
                'cycle_time': possibilities[i]['cycle_time'],
                'green_time': possibilities[i]['green_time'],
                'red_time': possibilities[i]['red_time'],
                'performance': performance}

        elif buffer['performance'] <= performance:
            continue

        elif buffer['performance'] > performance:
            buffer = {
                'cycle_time': possibilities[i]['cycle_time'],
                'green_time': possibilities[i]['green_time'],
                'red_time': possibilities[i]['red_time'],
                'performance': performance,
                'i': i}

    delete_files(file_name=file_name, period=period)
    timing = [buffer['green_time'],
              bfConst.YELLOW_DURATION,
              buffer['red_time'],
              bfConst.YELLOW_DURATION]

    execute_tl_attempt(file_name=file_name, period=period, timing=timing, tl_states=tl_states)
    print(buffer)


def plot_two_graphs(input_file_path_1: str, input_file_path_2: str, output_file: str, title: str = '',
                    line_1_legend: str = '', line_2_legend: str = ''):
    # Read info from both files
    y_axis_data_1 = get_data_from_file_path(file_path=input_file_path_1, opt=Const.Y_OPTION)
    x_axis_data_1 = get_data_from_file_path(file_path=input_file_path_1, opt=Const.X_OPTION)

    y_axis_data_2 = get_data_from_file_path(file_path=input_file_path_2, opt=Const.Y_OPTION)
    x_axis_data_2 = get_data_from_file_path(file_path=input_file_path_2, opt=Const.X_OPTION)

    # Plot both graphs into the same plane
    matplotlib.pyplot.plot(x_axis_data_1, y_axis_data_1, label=line_1_legend)
    matplotlib.pyplot.plot(x_axis_data_2, y_axis_data_2, label=line_2_legend)

    # Add legend
    matplotlib.pyplot.legend()

    # Title format
    title_font_style = {'family': 'sans-serif',
                        'fontname': 'Verdana',
                        'color': 'darkred',
                        'weight': 'bold',
                        'size': 16}

    # Title text
    matplotlib.pyplot.title(title, fontdict=title_font_style)

    # Label format
    label_font_style = {'family': 'sans-serif',
                        'fontname': 'Arial',
                        'color': 'black',
                        'weight': 'normal',
                        'size': 12}

    # Label text
    matplotlib.pyplot.xlabel(Const.PLOT_AXIS_LABEL_OPTIONS[Const.X_OPTION], fontdict=label_font_style)
    matplotlib.pyplot.ylabel(Const.PLOT_AXIS_LABEL_OPTIONS[Const.Y_OPTION], fontdict=label_font_style)

    # Add grid lines
    matplotlib.pyplot.grid()

    matplotlib.pyplot.savefig(output_file)

    # Close file and free from memory
    matplotlib.pyplot.close()


def script_run_plot(file_name: str, period: float):
    """
        Gather the data from the output, and print it.
        Does not run or setup any simulations.
    """
    # Set working dir to src
    SH.set_working_directory()

    # Get y data
    y_full_data = get_data_from_all_simulations_output(file_name, Const.Y_OPTION, period)
    y_data = SH.get_average_from_list_of_lists(y_full_data)

    # Get x data
    x_data = [x for x in range(SH.get_size_of_smallest_list(y_full_data))]

    # Get max and min vectors
    max_min_dictionary = SH.get_max_min_vectors_from_list_of_lists(y_full_data)
    maximums_vector = max_min_dictionary['maximum']
    minimums_vector = max_min_dictionary['minimum']

    # Plot data
    SH.plot_data(x_data, y_data, Const.X_OPTION, Const.Y_OPTION, file_name, period,
                 Const.FILL_MAX_MIN, maximums_vector, minimums_vector)
