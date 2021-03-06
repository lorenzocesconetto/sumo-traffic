from sumoTools.TrafficLight import TrafficLight
from sumoTools.TrafficLight import TrafficLightsSet
import sumoTools.geneticAlgorithmHelpers as GA
import copy
import random


def test1():
    tl_1 = TrafficLight()
    tl_1.id = 'tl_1'
    tl_1.state_and_duration = {'Gr': 41, 'yr': 4, 'rG': 41, 'ry': 4}
    tl_1.offset = 15

    tl_2 = copy.deepcopy(tl_1)
    tl_2.id = 'tl_2'
    tl_2.offset = 13

    tl_set_1 = TrafficLightsSet([tl_1, tl_2])

    ####################################################################
    tl_3 = TrafficLight()
    tl_3.id = 'tl_1'
    tl_3.state_and_duration = {'Gr': 27, 'yr': 4, 'rG': 60, 'ry': 4}
    tl_3.offset = 10

    tl_4 = copy.deepcopy(tl_1)
    tl_4.id = 'tl_2'
    tl_4.offset = 17

    tl_set_2 = TrafficLightsSet([tl_3, tl_4])

    ####################################################################
    best = [tl_set_1, tl_set_2]
    print(best)


def test2():
    iterable = [['a', 1], ['b', 2], ['c', 3]]
    for a, b in iterable:
        print(a + ' : ' + str(b))


def test3():
    tl_1 = TrafficLight()
    tl_1.id = 'tl_1'
    tl_1.state_and_duration = {'Gr': 41, 'yr': 4, 'rG': 41, 'ry': 4}
    tl_1.offset = 150

    tl_1.convert_from_int_to_binary()
    tl_1.convert_from_binary_to_int()

    print(tl_1)


def test4():
    number_of_bits = 4
    print(('{0:0' + str(number_of_bits) + 'b}').format(10))


if __name__ == '__main__':
    test4()
