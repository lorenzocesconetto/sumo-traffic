from sumoTools import gaConstants as gaConst
from sumoTools import Constants as Const
import random
import sys


class TrafficLight:
    def __init__(self):
        self.id = ''
        self.state_and_duration = dict()
        self.offset = 0
        self.cycle_time = 0

    number_of_bits = 8

    def __str__(self) -> str:
        return self.id + ': cycle_time=' + str(self.cycle_time) + ' offset=' + str(self.offset) + ' ' + \
               str(self.state_and_duration)

    def __repr__(self) -> str:
        return self.id + ': cycle_time=' + str(self.cycle_time) + ' offset=' + str(self.offset) + ' ' + \
               str(self.state_and_duration)

    @classmethod
    def make_random_tl(cls, tl_id: str, states: list):
        traffic_light = cls()
        traffic_light.id = tl_id

        for state in states:
            traffic_light.state_and_duration[state] = \
                random.randint(gaConst.MIN_PHASE_DURATION, gaConst.MAX_PHASE_DURATION)

        traffic_light.set_cycle_time_from_int()

        traffic_light.offset = random.randint(0, traffic_light.cycle_time - 1)

        return traffic_light

    def randomize_tl(self):
        for key in self.state_and_duration.keys():
            if 'y' not in key:
                self.state_and_duration[key] = random.randint(gaConst.MIN_PHASE_DURATION, gaConst.MAX_PHASE_DURATION)

        self.set_cycle_time_from_int()
        self.offset = random.randint(0, self.cycle_time - 1)

    def convert_from_int_to_binary(self):
        if self.offset > int('1' * self.number_of_bits, 2):
            self.offset = int('1' * self.number_of_bits, 2)
        self.offset = ('{0:0' + str(self.number_of_bits) + 'b}').format(self.offset)

        for key, value in self.state_and_duration.items():
            if 'y' in key:
                continue
            if value > int('1' * self.number_of_bits, 2):
                value = int('1' * self.number_of_bits, 2)
            self.state_and_duration[key] = ('{0:0' + str(self.number_of_bits) + 'b}').format(value)

    def convert_from_binary_to_int(self):
        self.offset = int(self.offset, 2)

        for key, value in self.state_and_duration.items():

            if 'y' in key:
                continue

            self.state_and_duration[key] = int(value, 2)

            if self.state_and_duration[key] < gaConst.MIN_PHASE_DURATION:
                self.state_and_duration[key] = gaConst.MIN_PHASE_DURATION

            if self.state_and_duration[key] > gaConst.MAX_PHASE_DURATION:
                self.state_and_duration[key] = gaConst.MAX_PHASE_DURATION

        self.set_cycle_time_from_int()

    def set_cycle_time_from_int(self):
        if (type(self.cycle_time) is not int) or (type(self.offset) is not int):
            print('Must be applied to an int')
            sys.exit(1)

        total_time = 0
        for value in self.state_and_duration.values():
            total_time += int(value)

        self.cycle_time = total_time
        while self.offset < 0:
            self.offset += self.cycle_time
        self.offset = self.offset % self.cycle_time


class TrafficLightsSet:
    def __init__(self, tl_list: list):
        self.performance = None
        self.traffic_light_list = tl_list

    def __str__(self):
        text = 'Performance=' + str(self.performance) + '\n'
        for tl in self.traffic_light_list:
            text = text + 'tl=' + tl.id + ': cycle_time=' + str(tl.cycle_time) + \
                   ' offset=' + str(tl.offset) + ' ' + str(tl.state_and_duration) + '\n'
        return text

    def __repr__(self):
        text = 'Performance=' + str(self.performance) + '\n'
        for tl in self.traffic_light_list:
            text = text + 'tl=' + tl.id + ': cycle_time=' + str(tl.cycle_time) + \
                   ' offset=' + str(tl.offset) + ' ' + str(tl.state_and_duration) + '\n'
        return text

    # @ class method
    # def make_tl_set(cls, tl_list: list):
    #     tl_set = cls()
    #     tl_set.traffic_light_list = tl_list
    #     return tl_set



