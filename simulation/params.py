# Simulation constant parameters

DEFAULT_WAIT_TIME = 1.0 # in seconds
DEFAULT_SPEED = 1.0 # floors per sec
DEFAULT_LAMBDA = 0.1 # average of requests per second, for poisson proces
FLOORS = tuple(range(1, 6)) # floors 1 to 5
SIMULATION_DURATION = 100 # in seconds
DEFAULT_BASE_FLOOR = 1 # starting floor, "street level"
BASE_FLOOR_WEIGHT = 5 # how many times base floor is more likely to be requested
DEFAULT_CHECK_TIME = 0.5 # every how many seconds the elevator checks for new tasks