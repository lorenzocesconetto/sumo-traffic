import sumoTools.simulationHelpers as SH
import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import sumoTools.simulationConstants as Const
import matplotlib.pyplot


STATES_ARRAY = ['GrrG', 'yrry', 'rGGr', 'ryyr']
# tl_configuration_timing = [10, 2, 10, 2]


def make_tl_name(period: float, i: int):
    return Const.TL_FILE + '-' + str(period) + '-' + str(i) + Const.TL_FILE_EXTENSION


def create_tl_dir(file_name: str):
    """
        Create a directory to take all the additional files
        to the traffic light.
    """
    SH.set_working_directory()

    for directory in [Const.TL_DIR, Const.OUT_DIR, Const.CFG_DIR, Const.PLOT_DIR]:
        if not os.path.isdir(os.path.join(file_name, directory)):
            subprocess.run(['mkdir', os.path.join(file_name, directory)])


def generate_possibilities():
    """
        Generate a list of tuples in the format [ (cycle_time, green_time, red_time), (...) ... ]
        which represents all possible programs.
        It also limits the red time so we can reduce the number of possibilities based
        on what we know
    """
    yellow_duration = Const.NUMBER_OF_YELLOW_PHASES * Const.YELLOW_DURATION

    # Check if numbers are valid
    if (
        (yellow_duration + Const.NUMBER_OF_RED_GREEN_PHASES * Const.MIN_PHASE_DURATION) > Const.MAX_CYCLE
            or (yellow_duration + Const.NUMBER_OF_RED_GREEN_PHASES * Const.MAX_PHASE_DURATION) < Const.MIN_CYCLE
            or Const.MIN_CYCLE > Const.MAX_CYCLE
    ):
        print('Invalid cycle values. Please check numbers.\n')
        sys.exit(1)

    # Create list to be returned
    possibilities = []

    # Iterate possible values
    for cycle_time in range(Const.MIN_CYCLE, Const.MAX_CYCLE + 1):

        minimum_time = cycle_time - yellow_duration - Const.MAX_PHASE_DURATION * (Const.NUMBER_OF_RED_GREEN_PHASES - 1)
        maximum_time = cycle_time - yellow_duration - Const.MIN_PHASE_DURATION * (Const.NUMBER_OF_RED_GREEN_PHASES - 1)

        for green_time in range(
                max(Const.MIN_PHASE_DURATION, minimum_time),
                1 + min(Const.MAX_PHASE_DURATION, maximum_time)):

            red_time = cycle_time - green_time - yellow_duration

            if red_time <= Const.MAX_RED_TIME:
                possibilities.append((cycle_time, green_time, red_time))

    return possibilities


def create_tl_program_file(file_name: str, timing: list, states: list, i: int, period: float):
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

    with open(os.path.join(file_name, Const.TL_DIR, make_tl_name(period=period, i=i)), 'w') as file:
        file.write('<additional>\n')
        file.write('\t<tlLogic id="gneJ3" type="static" programID="my_program" offset="0">\n')
        for i in range(Const.NUMBER_OF_PHASES):
            file.write('\t\t<phase duration="' + str(timing[i]) + '" state="' + states[i] + '"/>\n')
        file.write('\t</tlLogic>\n')
        file.write('</additional>\n')
    file.closed


def create_cfg_and_add_tl_program(file_name: str, period: float, i: int):

    network = file_name + '.net.xml'
    if not os.path.isfile(file_name + '/' + network):
        print('Network not found: ' + network)
        sys.exit(1)

    name = SH.generate_complete_name_with_index(file_name, period, Const.FILE_NUMBER)
    route_file_path = os.path.join(file_name, Const.ROUTE_DIR, name) + Const.ROUTE_FILE_EXTENSION

    if not os.path.isfile(route_file_path):
        print('Route file not found: ' + route_file_path)
        sys.exit(1)

    # Open XML in memory
    base = ET.parse(Const.BASE_CFG)

    # Set network input
    base.find('input/net-file').set('value', '../' + network)

    # Set route input
    base.find('input/route-files').set('value', '../' + Const.ROUTE_DIR + '/' + name + Const.ROUTE_FILE_EXTENSION)

    # Set output file
    output = base.find('output')
    ET.SubElement(output, Const.OUTPUT,
                  {'value': os.path.join('..', Const.OUT_DIR,
                                         SH.generate_complete_name_with_index(file_name, period, i)
                                         + Const.OUT_FILE_EXTENSION)})

    # Add Traffic Light program
    cfg_file_buffer = base.find('input')
    ET.SubElement(cfg_file_buffer, Const.ADDITIONAL_FILE_TAG,
                  {'value': os.path.join('..', Const.TL_DIR,
                                         make_tl_name(period=period, i=i))})

    # Save configuration xml to file
    base.write(os.path.join(file_name, Const.CFG_DIR,
                            SH.generate_complete_name_with_index(file_name, period, i) + Const.CFG_FILE_EXTENSION))


def run_simulation_tl(file_name: str, period: float, i: int = 0):
    """
        Runs simulation for that file_name for a period and number files.
        Saves to cfg directory
    """
    complete_name = SH.generate_complete_name_with_index(file_name, period, i)
    subprocess.run(['sumo', '-c', os.path.join(file_name, Const.CFG_DIR, complete_name + Const.CFG_FILE_EXTENSION)])


def get_data(file_name: str, period: float, i: int, opt: str):
    """
        Get data from a single *.out.xml file and return it into a list.
        Parameter opt could be: depart, departDelay, meanWaitingTime, etc.
        Returns [x1, x2, ...]
    """
    name = os.path.join(file_name, Const.OUT_DIR,
                        SH.generate_complete_name_with_index(file_name, period, i) + Const.OUT_FILE_EXTENSION)

    if not os.path.isfile(name):
        print('Could not find file: ' + name)
        sys.exit(1)

    data = []

    # Open xml file
    root = ET.parse(name).getroot()

    for child in root:
        data.append(float(child.get(opt)))

    return data


def get_data_from_file_path(file_path: str, opt: str):
    data = []

    # Open xml file
    root = ET.parse(file_path).getroot()

    for child in root:
        data.append(float(child.get(opt)))

    return data


def measure_performance(data):
    number_of_elements = len(data)

    total_sum = 0
    for num in data:
        total_sum += num

    return total_sum / number_of_elements


def delete_files(file_name: str, period: float, i: int):
    """
        Deletes output and cfg files.
        Doesn't return anything
    """
    SH.set_working_directory()
    name = SH.generate_complete_name_with_index(file_name, period, i)

    out_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, Const.OUT_DIR, name + Const.OUT_FILE_EXTENSION)
    cfg_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, Const.CFG_DIR, name + Const.CFG_FILE_EXTENSION)
    tl_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, Const.TL_DIR, make_tl_name(period=period, i=i))

    files = [out_file_path, cfg_file_path, tl_file_path]

    for file in files:
        if os.path.isfile(file):
            os.remove(file)
        else:
            print('File to be deleted not found: ' + file + '\n')
            sys.exit(1)


def pick_the_best_tl_program(file_name: str, period: float):
    cycle_time_index = 0
    green_time_index = 1
    red_time_index = 2

    SH.set_working_directory()
    create_tl_dir(file_name)
    possibilities = generate_possibilities()

    buffer = None
    for i in range(len(possibilities)):
        timing = [possibilities[i][green_time_index],
                  Const.YELLOW_DURATION,
                  possibilities[i][red_time_index],
                  Const.YELLOW_DURATION]

        create_tl_program_file(file_name=file_name, timing=timing, states=STATES_ARRAY, i=i, period=period)
        create_cfg_and_add_tl_program(file_name=file_name, period=period, i=i)
        run_simulation_tl(file_name=file_name, period=period, i=i)
        data = get_data(file_name=file_name, period=period, i=i, opt=Const.Y_OPTION)
        performance = measure_performance(data)

        if buffer is not None and buffer['performance'] < performance:
            delete_files(file_name=file_name, period=period, i=i)

        elif buffer is None or buffer['performance'] > performance:
            if buffer is not None:
                delete_files(file_name=file_name, period=period, i=buffer['i'])
            buffer = {
                'cycle_time': possibilities[i][cycle_time_index],
                'green_time': possibilities[i][green_time_index],
                'red_time': possibilities[i][red_time_index],
                'performance': performance,
                'i': i}

    print(buffer)


def script_run_brute_force(file_name: str, period: float):
    print('Numero de possibildades a serem executadas: ' + str(len(generate_possibilities())) + '\n')
    choice = input('Deseja continuar? (s) ou (n)\n')
    if choice.lower()[0] == 's':
        period = float(period)
        pick_the_best_tl_program(file_name=file_name, period=period)


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
