from typing import List
import sys
sys.path.append("..")
from sumoTools import gaConstants as gaConst
from sumoTools import Constants as Const
from sumoTools import simulationHelpers as SH
from sumoTools.TrafficLight import TrafficLight
from sumoTools.TrafficLight import TrafficLightsSet
import os
import subprocess
import xml.etree.ElementTree
import matplotlib.pyplot
import random
import copy


####################
# Low level Helpers
####################
def check_timing_constraints():
    if gaConst.STOP_CRITERIA_ITERATIONS > gaConst.MAXIMUM_ITERATIONS:
        print('Number of max iterations should be equal to or larger than number of iterations for stopping criteria')
        sys.exit(1)

    yellow_duration = gaConst.NUMBER_OF_YELLOW_PHASES * gaConst.YELLOW_DURATION

    # Check if numbers are valid
    if (
            yellow_duration + gaConst.NUMBER_OF_RED_GREEN_PHASES * gaConst.MIN_PHASE_DURATION > gaConst.MAX_CYCLE
            or yellow_duration + gaConst.NUMBER_OF_RED_GREEN_PHASES * gaConst.MAX_PHASE_DURATION < gaConst.MIN_CYCLE
            or gaConst.MIN_CYCLE > gaConst.MAX_CYCLE):
        print('Invalid cycle values. Please check numbers.\n')
        sys.exit(1)


def make_tl_name(period: float):
    return Const.TL_FILE + '-' + str(period) + Const.TL_FILE_EXTENSION


def create_ga_dir(file_name: str):
    """
        Create a directory to take all the additional files
        to the traffic light.
    """
    SH.set_working_directory()

    for directory in [Const.TL_DIR, gaConst.OUT_DIR_GA, gaConst.CFG_DIR_GA, Const.PLOT_DIR]:
        if not os.path.isdir(os.path.join(file_name, directory)):
            subprocess.run(['mkdir', os.path.join(file_name, directory)])


def create_tl_program_file(file_name: str, tls_objects_list: List[TrafficLight], period: float) -> None:
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
    period = float(period)

    file = open(os.path.join(Const.WORKING_DIRECTORY, file_name, Const.TL_DIR, make_tl_name(period=period)), 'w')
    file.write('<additional>\n')
    for tl in tls_objects_list:
        file.write('    <tlLogic id="' + tl.id + '" type="static" programID="my_program" offset="' + str(tl.offset) + '">\n')
        for state, duration in tl.state_and_duration.items():
            file.write('        <phase duration="' + str(duration) + '" state="' + state + '"/>\n')
        file.write('    </tlLogic>\n')

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
                      {'value': os.path.join('..', gaConst.OUT_DIR_GA,
                                             SH.generate_complete_name_with_index(file_name, period, i)
                                             + Const.OUT_FILE_EXTENSION)})

        # Add Traffic Light program
        cfg_file_buffer = base.find('input')
        xml.etree.ElementTree.SubElement(cfg_file_buffer, Const.ADDITIONAL_FILE_TAG,
                                         {'value': os.path.join('..', Const.TL_DIR,
                                                                make_tl_name(period=period))})

        # Save configuration xml to file
        base.write(os.path.join(file_name, gaConst.CFG_DIR_GA,
                                SH.generate_complete_name_with_index(file_name, period, i)
                                + Const.CFG_FILE_EXTENSION))


def run_simulation_ga(file_name: str, period: float):
    """
        Runs simulation for that file_name for a period and number files.
        Saves to cfg directory
    """
    for i in range(Const.NUMBER_OF_SIMULATIONS):
        complete_name = SH.generate_complete_name_with_index(file_name, period, i)
        subprocess.run(['sumo', '--no-warnings', '-c',
                        os.path.join(Const.WORKING_DIRECTORY, file_name,
                                     gaConst.CFG_DIR_GA, complete_name + Const.CFG_FILE_EXTENSION)])


def execute_tl_attempt(file_name: str, period: float, tls_objects_list: List[TrafficLight]):
    create_tl_program_file(file_name=file_name, tls_objects_list=tls_objects_list, period=period)
    create_cfg_and_add_tl_program(file_name=file_name, period=period)
    run_simulation_ga(file_name=file_name, period=period)


def measure_performance(data):
    """ Measures performance based on a list of lists """
    total_sum = 0

    for d in data:
        total_sum += max(d)

    return total_sum / len(data)


def get_data(file_name: str, period: float, i: int, opt: str):
    """
        Get data from a single *.out.xml file and return it into a list.
        Parameter opt could be: depart, departDelay, meanWaitingTime, etc.
        Returns [x1, x2, ...]
    """
    name = os.path.join(file_name, gaConst.OUT_DIR_GA,
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
        name = os.path.join(Const.WORKING_DIRECTORY, file_name, gaConst.OUT_DIR_GA,
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

        out_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, gaConst.OUT_DIR_GA,
                                     name + Const.OUT_FILE_EXTENSION)

        cfg_file_path = os.path.join(Const.WORKING_DIRECTORY, file_name, gaConst.CFG_DIR_GA,
                                     name + Const.CFG_FILE_EXTENSION)

        files = [out_file_path, cfg_file_path]

        for file in files:
            if os.path.isfile(file):
                os.remove(file)
            else:
                print('File to be deleted not found: ' + file + '\n')
                sys.exit(1)


def make_probability_vector():
    probability_vector = []
    for i in range(gaConst.KEEP_POPULATION):
        for j in range(gaConst.KEEP_POPULATION - i):
            probability_vector.append(i)
    return probability_vector


def plot_evolution_graph(best_performances: List[float], average_performances: List[float], output_path: str,
                         title: str = '', best_legend: str = '', average_legend: str = ''):
    if len(best_performances) != len(average_performances):
        print('The vectors that hold best performance and average performance have different lengths')
        print('Something went wrong, please check')
        sys.exit(1)

    # x axis data
    x_axis_data = [x + 1 for x in range(len(best_performances))]

    # Plot both graphs into the same plane
    matplotlib.pyplot.plot(x_axis_data, average_performances, label=average_legend)
    matplotlib.pyplot.plot(x_axis_data, best_performances, label=best_legend)

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
    matplotlib.pyplot.xlabel('Geração', fontdict=label_font_style)
    matplotlib.pyplot.ylabel(Const.PLOT_AXIS_LABEL_OPTIONS[Const.Y_OPTION], fontdict=label_font_style)

    # Add grid lines
    matplotlib.pyplot.grid()

    if output_path:
        matplotlib.pyplot.savefig(output_path)
    else:
        matplotlib.pyplot.show()

    # Close file and free from memory
    matplotlib.pyplot.close()


####################
# Mid level Helpers
####################
def read_tls_ids_states(file_name: str):
    """
        Returns an object with traffic light id and states
        [
            gneJ3 : {'Gr': '41', 'yr': '4', 'rG': '41', 'ry': '4'}
            gneJ4 : {'Gr': '41', 'yr': '4', 'rG': '41', 'ry': '4'} ...
        ]
    """
    path_to_network_file = os.path.join(Const.WORKING_DIRECTORY, file_name, file_name + Const.NET_FILE_EXTENSION)
    base = xml.etree.ElementTree.parse(path_to_network_file)

    tls_objects_list: List[TrafficLight] = []
    traffic_lights = base.findall('tlLogic')
    for traffic_light in traffic_lights:

        # Skip repeated id's
        if any(x.id == traffic_light.attrib['id'] for x in tls_objects_list):
            continue

        # create new TL object
        new_tl = TrafficLight()
        new_tl.id = traffic_light.attrib['id']
        new_tl.offset = int(traffic_light.attrib['offset'])
        for phase_element in traffic_light:
            new_tl.state_and_duration[phase_element.attrib['state']] = int(phase_element.attrib['duration'])

        new_tl.set_cycle_time_from_int()
        tls_objects_list.append(new_tl)

    return tls_objects_list


def do_simulations(file_name: str, period: float, tl_set: TrafficLightsSet):
    """ Execute simulations, measures the performance, and attachs to the object """
    execute_tl_attempt(file_name=file_name, period=period, tls_objects_list=tl_set.traffic_light_list)
    data = get_data_from_all_simulations_output(file_name=file_name, opt=Const.Y_OPTION, period=period)

    performance = measure_performance(data)

    if performance <= 0:
        print('Invalid performance: Performance = ' + str(performance))
        sys.exit(1)

    tl_set.performance = performance


####################
# Genetic Algorithm Helpers
####################
def select_chromosomes_to_crossover():
    probability_vector = make_probability_vector()
    chromosomes_to_crossover = []
    number_of_matches = int(gaConst.NUMBER_OF_CHILDREN / 2)

    for i in range(number_of_matches):
        size = len(probability_vector) - 1
        selection_one = probability_vector[random.randint(0, size)]
        selection_two = probability_vector[random.randint(0, size)]
        chromosomes_to_crossover.append([selection_one, selection_two])

    return chromosomes_to_crossover


def switch_genetic_material(gen_1: str, gen_2: str):
    if len(gen_1) != len(gen_2):
        print('chromosomes with different length')
        sys.exit(1)

    switch_point = random.randint(0, len(gen_1) - 1)

    gen_1_transfer = gen_1[switch_point:]
    gen_2_transfer = gen_2[switch_point:]

    gen_1 = gen_1[:switch_point] + gen_2_transfer
    gen_2 = gen_2[:switch_point] + gen_1_transfer

    return gen_1, gen_2


def mutation(chromosome: str):
    mutation_position = random.randint(0, len(chromosome) - 1)
    new_gen = '1' if chromosome[mutation_position] == '0' else '0'
    chromosome = chromosome[:mutation_position] + new_gen + chromosome[mutation_position + 1:]

    return chromosome


####################
# Genetic Algorithm functions
####################
def initial_population(file_name: str) -> List[TrafficLightsSet]:
    initial_pop = []
    for i in range(gaConst.POPULATION_SIZE):
        tls_objects_list = read_tls_ids_states(file_name=file_name)
        individual = []
        for traffic_light in tls_objects_list:
            traffic_light.randomize_tl()
            individual.append(traffic_light)
        initial_pop.append(TrafficLightsSet(individual))

    return initial_pop


def fitness_function(file_name: str, period: float, tl_set: TrafficLightsSet):
    """ Appends performance to the object TrafficLightSet """
    respects_constraints = True

    for tl in tl_set.traffic_light_list:
        if tl.cycle_time > gaConst.MAX_CYCLE or tl.cycle_time < gaConst.MIN_CYCLE:
            respects_constraints = False

        for state, duration in tl.state_and_duration.items():
            if 'y' not in state:
                if duration > gaConst.MAX_PHASE_DURATION or duration < gaConst.MIN_PHASE_DURATION:
                    respects_constraints = False

    if respects_constraints:
        do_simulations(file_name=file_name, period=period, tl_set=tl_set)
    else:
        tl_set.performance = gaConst.PERFORMANCE_PENALTY


def filter_chromosomes_to_keep(population: List[TrafficLightsSet]):
    population.sort(key=lambda x: x.performance, reverse=False)
    population = population[:gaConst.KEEP_POPULATION]

    return population


def stop_iterations(best_performance_each_generation: List[float]):
    """Check if the stopping criteria was met"""
    if len(best_performance_each_generation) < gaConst.STOP_CRITERIA_ITERATIONS:
        return False

    last_performance = best_performance_each_generation[-1]
    base_performance = best_performance_each_generation[-gaConst.STOP_CRITERIA_ITERATIONS]

    if (base_performance - last_performance) / base_performance < gaConst.STOP_CRITERIA_ENHANCEMENT:
        return True
    else:
        return False


def cross_over(population: List[TrafficLightsSet]):

    population2 = copy.deepcopy(population)

    chromosomes_to_crossover = select_chromosomes_to_crossover()
    children = []

    for parent_one_index, parent_two_index in chromosomes_to_crossover:
        parent_one = copy.deepcopy(population2[parent_one_index])
        parent_two = copy.deepcopy(population2[parent_two_index])

        for tl_1, tl_2 in zip(parent_one.traffic_light_list, parent_two.traffic_light_list):
            # Convert to binary
            tl_1.convert_from_int_to_binary()
            tl_2.convert_from_int_to_binary()

            # Make cross over for the offset
            tl_1.offset, tl_2.offset = switch_genetic_material(tl_1.offset, tl_2.offset)

            # Make cross over for each phase duration
            for (phase_1_key_state, phase_1_value_duration), (phase_2_key_state, phase_2_value_duration) in \
                    zip(tl_1.state_and_duration.items(), tl_2.state_and_duration.items()):

                tl_1.state_and_duration[phase_1_key_state], tl_2.state_and_duration[phase_2_key_state] = \
                    switch_genetic_material(phase_1_value_duration, phase_2_value_duration)

            # Back to the int version
            tl_1.convert_from_binary_to_int()
            tl_2.convert_from_binary_to_int()

        children.append(copy.deepcopy(parent_one))
        children.append(copy.deepcopy(parent_two))

    for tl_set in children:
        tl_set.performance = None

    return children


def mutate_chromosomes(population: List[TrafficLightsSet]):
    for tl_set in population:
        for tl in tl_set.traffic_light_list:
            tl.convert_from_int_to_binary()

            if random.random() < gaConst.MUTATION_PROBABILITY:
                tl.offset = mutation(tl.offset)
                tl_set.performance = None

            for phase_state, phase_duration in tl.state_and_duration.items():
                if 'y' not in phase_state:
                    if random.random() < gaConst.MUTATION_PROBABILITY:
                        tl.state_and_duration[phase_state] = mutation(phase_duration)
                        tl_set.performance = None

            tl.convert_from_binary_to_int()


def get_population_avg_and_best(population: List[TrafficLightsSet]):

    filtered_performance = [tl_set.performance for tl_set in population
                            if tl_set.performance != gaConst.PERFORMANCE_PENALTY]

    if len(filtered_performance) <= gaConst.NUMBER_OF_CHILDREN:
        print('Most of the population was discarded in the timing constraints criteria')
        print('Please reconsider changing the constants at gaConstants.py')
        sys.exit(1)

    best_performance = min(filtered_performance)
    average_performance = sum(x for x in filtered_performance) / len(filtered_performance)

    return {'best': best_performance, 'average': average_performance}


def get_best_chromosome(population: List[TrafficLightsSet]):
    best = min(population, key=lambda x: x.performance)

    if best.performance == gaConst.PERFORMANCE_PENALTY:
        print('The best chromosome doesnt respect constraints.\n')
        print('Please review the timing settings in the gaConstants.py file.\n')
        sys.exit(1)

    return copy.deepcopy(best)


def main(file_name: str, period: float):
    # Creates Genetic Algorithm directories
    create_ga_dir(file_name=file_name)

    # Checks time Constraints
    check_timing_constraints()

    # Generate route files
    SH.generate_random_route_files(file_name=file_name, period=period)

    # Create lists to store the population average and best performance
    best_performance_each_generation = []
    average_performance_each_generation = []
    best_chromosome_each_generation = []

    # Generate initial population
    population = initial_population(file_name=file_name)

    for i in range(gaConst.MAXIMUM_ITERATIONS):
        for tl_set in population:
            if tl_set.performance is None:
                fitness_function(file_name=file_name, period=period, tl_set=tl_set)

        # Store the best and the average performance of population
        avg_n_best = get_population_avg_and_best(population)
        best_performance_each_generation.append(avg_n_best['best'])
        average_performance_each_generation.append(avg_n_best['average'])
        # Store the best chromosome
        best_chromosome_each_generation.append(get_best_chromosome(population))

        # Check if the stopping criteria was met
        if stop_iterations(best_performance_each_generation):
            print('Stop criteria met')
            print('Number of iterations: ' + str(i + 1))
            break

        # Remove the bad performing individuals (the weak ones)
        population = filter_chromosomes_to_keep(population)

        # Cross over (reproduce) the remaining individuals (the strong ones)
        children = cross_over(population)

        # Small change of each new individual have some genes mutated
        mutate_chromosomes(children)

        population = population + children


    i = 0
    while os.path.isfile(os.path.join(Const.WORKING_DIRECTORY, file_name, file_name + '-' + str(period) + '-' + str(i) + '.txt'))\
            or os.path.isfile(os.path.join(Const.WORKING_DIRECTORY, file_name, file_name + '-' + str(period) + '-' + str(i) + '.png')):
        i += 1

    name = os.path.join(Const.WORKING_DIRECTORY, file_name, file_name + '-' + str(period) + '-' + str(i))
    log = open(name + '.txt', 'w')
    log.write('Best performance for each generation: ' + str(best_performance_each_generation) + '\n')
    log.write('Average performance for each generation: ' + str(average_performance_each_generation) + '\n')
    log.write('Best chromosome for each generation: ' + str(best_chromosome_each_generation) + '\n')

    plot_evolution_graph(best_performances=best_performance_each_generation,
                         average_performances=average_performance_each_generation,
                         output_path=name + '.png',
                         title='Evolução da performance (p=' + str(period) + ')',
                         best_legend='Melhor performance por geração',
                         average_legend='Média da performance por geração')


if __name__ == '__main__':
    for i in range(3):
        main(file_name='principal_test', period=1.0)


