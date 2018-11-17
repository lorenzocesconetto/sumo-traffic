####################
# Genetic Algorithm Constants
####################

MAXIMUM_ITERATIONS = 1
POPULATION_SIZE = 4

STOP_CRITERIA_ENHANCEMENT = 0.05
STOP_CRITERIA_ITERATIONS = 1

# Probability to apply a genetic mutation
MUTATION_PROBABILITY = 0.01

# Number of individuals to keep from previous generation (ALWAYS ODD)
keep_helper = int(0.5 * POPULATION_SIZE)
KEEP_POPULATION = keep_helper if (POPULATION_SIZE - keep_helper) % 2 == 0 else keep_helper + 1

# Number of children
NUMBER_OF_CHILDREN = POPULATION_SIZE - KEEP_POPULATION

# Directories
CFG_DIR_TL = 'cfg-tl'
OUT_DIR_TL = 'out-tl'

# Timing Constraints
YELLOW_DURATION = 4  # in seconds
NUMBER_OF_YELLOW_PHASES = 2
NUMBER_OF_RED_GREEN_PHASES = 2
NUMBER_OF_PHASES = NUMBER_OF_YELLOW_PHASES + NUMBER_OF_RED_GREEN_PHASES

MIN_PHASE_DURATION = 8  # in seconds
MAX_PHASE_DURATION = 70  # in seconds

MAX_CYCLE = 130  # in seconds
MIN_CYCLE = 40  # in seconds

PERFORMANCE_PENALTY = 999999

# Dirs
OUT_DIR_GA = 'out-ga'
CFG_DIR_GA = 'cfg-ga'
