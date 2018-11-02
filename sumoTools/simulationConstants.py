####################
# Simulation Helpers
####################

# Number of simulations
NUMBER_OF_SIMULATIONS = 1

# Directory for PLOT and SIMULATIONS
OUT_DIR = 'out'
PLOT_DIR = 'plot'

# Directories for SIMULATIONS only
ROUTE_DIR = 'route'
CFG_DIR = 'cfg'

# Simulation
X_OPTION = 'time'
Y_OPTION = 'meanWaitingTime'
OUTPUT = 'summary-output'  # summary-output tripinfo-output
STEP = 1
FILL_MAX_MIN = True
ROUTE_GENERATION_OPTIONS = {
                            # 'max-distance': 300,
                            'min-distance': 200,
                            'start': 0,
                            'end': 5400,
                            'fringe-factor': 10,
                            'speed-exponent': 4
                            }

####################
# Brute Force
####################
FILE_NUMBER = 0

YELLOW_DURATION = 2
NUMBER_OF_YELLOW_PHASES = 2
NUMBER_OF_RED_GREEN_PHASES = 2
NUMBER_OF_PHASES = NUMBER_OF_YELLOW_PHASES + NUMBER_OF_RED_GREEN_PHASES

ADDITIONAL_FILE_TAG = 'additional-files'

MIN_PHASE_DURATION = 8
MAX_PHASE_DURATION = 58

MAX_RED_TIME = 13
MIN_GREEN_TIME = 50

MAX_CYCLE = 80
MIN_CYCLE = 60

TL_DIR = 'traffic-lights'
TL_FILE = 'traffic_light'
TL_FILE_EXTENSION = '.tl.xml'

####################
# Never change
####################
ROUTE_FILE_EXTENSION = '.rou.xml'
OUT_FILE_EXTENSION = '.out.xml'
CFG_FILE_EXTENSION = '.sumo.cfg'
NET_FILE_EXTENSION = '.net.xml'
RANDOM_TRIPS_SCRIPT_PATH = '/Users/lorenzocesconetto/Applications/sumo-0.31.0/tools/randomTrips.py'
WORKING_DIRECTORY = '/Users/lorenzocesconetto/PyCharmProjects/sumo-tfc/src/'
BASE_CFG = 'base.sumo.cfg'
OUTPUT_OPTIONS = ['summary-output', 'tripinfo-output']
PLOT_AXIS_LABEL_OPTIONS = {'time': 'Time (s)',
                           'loaded': 'Total number of cars loaded (#)',
                           'inserted': 'Total number of cars inserted in the map (#)',
                           'running': 'Number of cars currently in the map (#)',
                           'waiting': 'Number of cars currently waiting at intersections (#)',
                           'ended': 'Total number of cars that left the map (#)',
                           'meanWaitingTime': 'Mean Waiting Time (s)',
                           'meanTravelTime': 'Mean Travel Time (s)',
                           'duration': 'Duration (?)',
                           'depart': 'Actual Period (s/veh)'}
