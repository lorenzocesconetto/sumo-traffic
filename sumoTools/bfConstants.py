####################
# Brute Force
####################
CFG_DIR_TL = 'cfg-tl'
OUT_DIR_TL = 'out-tl'

YELLOW_DURATION = 4  # in seconds
NUMBER_OF_YELLOW_PHASES = 2
NUMBER_OF_RED_GREEN_PHASES = 2
NUMBER_OF_PHASES = NUMBER_OF_YELLOW_PHASES + NUMBER_OF_RED_GREEN_PHASES

MIN_PHASE_DURATION = 8  # in seconds
MAX_PHASE_DURATION = 70  # in seconds

MAX_CYCLE = 90  # in seconds
MIN_CYCLE = 50  # in seconds

# In order to reduce the number of cases to simulate
MAX_RED_TIME = 10000  # in seconds
MIN_GREEN_TIME = 0  # in seconds
