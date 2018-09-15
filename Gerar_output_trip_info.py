import sys
import os
import subprocess
import xml.etree.ElementTree as ET
import argparse


def create_dir(file_name):
    dirs = ['cfg_trip', 'out_trip']
    abs_dirs = [file_name + '/' + x for x in dirs]
    for directory in abs_dirs:
        if not os.path.isdir(directory):
            subprocess.run(['mkdir', directory])


def create_cfg(file_name, period, number):
    for i in range(number):
        network = file_name + '.net.xml'
        name = file_name + '-' + str(period) + '-' + str(i)
        comp_name = file_name + '-' + str(period) + '-' + str(i) + '-trip'

        base = ET.parse('base_trip.sumo.cfg')
        base.find('input/net-file').set('value', '../' + network)
        base.find('input/route-files').set('value', '../route/' + name + '.rou.xml')
        base.find('output/tripinfo-output').set('value', '../out_trip/' + comp_name + '.out.xml')
        base.write(file_name + '/cfg_trip/' + comp_name + '.sumo.cfg')


def run_simulation(file_name, period, number):
    for i in range(number):
        comp_name = file_name + '-' + str(period) + '-' + str(i) + '-trip'
        subprocess.run(['sumo', '-c', file_name + '/cfg_trip/' + comp_name + '.sumo.cfg'])


def main(file_name, period, number):
    period = float(period)
    create_dir(file_name)
    create_cfg(file_name, period, number)
    run_simulation(file_name, period, number)


if __name__ == '__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('file_name', type=str)
    # parser.add_argument('period', type=float, default=1)
    # parser.add_argument('number', type=int, default=10)
    #
    # args = vars(parser.parse_args())
    #
    # main(**args)
    main('new_manhattan', 1, 10)
