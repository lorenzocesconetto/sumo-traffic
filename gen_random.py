import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import argparse


def gen_complete_name(file_name, period, i):
   return file_name + '-' + str(period) + '-' + str(i)


def checks(file_name, period, number):
    # Check if file_name dir exists
    if not os.path.isdir(file_name):
        print(f"Couldn't find directory named: {file_name}")
        sys.exit(1)

    # Check if the .net.xml file exists
    if not os.path.isfile(file_name + '/' + file_name + '.net.xml'):
        print("Couldn't find network file: " + file_name + '/' + file_name + '.net.xml')
        sys.exit(1)

    # Chek if n is valid
    if number <= 0 or number > 10:
        print("number must be positive and no larger than 10")
        sys.exit(1)

    # Check period value
    if period > 10 or period < 0.3:
        print("period must be between 0.3 and 10")
        sys.exit(1)


def create_dir(file_name):
    # check and create route dir
    dirs = ['route', 'cfg', 'out', 'plot']
    abs_dirs = [file_name + '/' + x for x in dirs]

    for dir in abs_dirs:
        if not os.path.isdir(dir):
            subprocess.run(['mkdir', dir])


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
    command.append('--end=5400')
    command.append('--period=' + str(period))
    command.append('-r')

    for i in range(number):
        # Append path for route file
        comp_name = gen_complete_name(file_name, period, i)
        route_name = file_name + '/route/' + comp_name + '.rou.xml'
        command.append(route_name)

        # Create route file
        subprocess.run(command)

        # Remove path route file
        command.pop()

        # Remove trash files
        del_name = file_name + '/route/' + comp_name + '.rou.alt.xml'
        subprocess.run(['rm', 'trips.trips.xml', del_name])


def create_cfg(file_name, period, number):
    # Setup configurations to create network
    cfg_file = 'base_summary.sumo.cfg'

    for i in range(number):
        comp_name = gen_complete_name(file_name, period, i)
        # Load in memory configuration file
        base = ET.parse(cfg_file)

        # Setup the config file
        base.find('input/net-file').set('value', '../' + file_name + '.net.xml')
        base.find('input/route-files').set('value', '../route/' + comp_name + '.rou.xml')
        base.find('output/summary-output').set('value', '../out/' + comp_name + '.out.xml')
        base.write(file_name + '/cfg/' + comp_name + '.sumo.cfg')


def run_simulation(file_name, period, number):
    for i in range(number):
        comp_name = gen_complete_name(file_name, period, i)
        # Run simulation
        subprocess.run(['sumo', '-c', file_name + '/cfg/' + comp_name + '.sumo.cfg'])


def gen_random(file_name, period=1, number=10):
    period = float(period)
    checks(file_name, period, number)
    create_dir(file_name)
    gen_random_trips(file_name, period, number)
    create_cfg(file_name, period, number)
    run_simulation(file_name, period, number)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name", help="Folder name", type=str)
    parser.add_argument("period", help="Period value", type=float, default=1)
    parser.add_argument("number", help="Number of random files of input to graph", type=int, default=10)
    args = parser.parse_args()

    gen_random(**vars(args))
