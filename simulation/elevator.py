from collections import deque
import simpy

from params import DEFAULT_WAIT_TIME, DEFAULT_CHECK_TIME


class Elevator:
    def __init__(self, env: simpy.Environment, floors: tuple[int], speed_floors_per_sec: float, base_floor: int):
        """
        Elevator agent, takes requests and moves across floors.

        Args:
            env: SimPy environment
            floors: Valid floor numbers (1, 2, 3, ..., 10)
            speed_floors_per_sec: Constant speed of elevator in floors per second
            base_floor: floor at street level, starting point
        """
        self.env = env
        self.floors = floors
        self.speed = speed_floors_per_sec
        self.base_floor = base_floor if base_floor in self.floors else None

        self.current_floor = base_floor
        self.task_queue = deque()
        self.moving = False

        # Start the elevator process
        self.process = env.process(self.run())

    def add_task(self, target_floor: int):
        """
        Enqueue a request to move to a specific floor.
        """
        if target_floor not in self.floors:
            raise ValueError(f"Invalid floor: {target_floor}")
        self.task_queue.append(target_floor)

    def hold(self, duration: float):
        """
        Elevator remains idle at current floor for a set duration.
        """
        yield self.env.timeout(duration)

    def move_to(self, target_floor: int):
        """
        Simulates elevator travel from current floor to target_floor.
        Uses constant speed to compute duration.
        """
        # Calculate travel time
        floor_diff = abs(self.current_floor - target_floor)
        if floor_diff == 0:
            return  # Already at floor
        travel_time = floor_diff / self.speed

        # Move event
        self.moving = True
        print(f"[{self.env.now:.1f}] Elevator starting move from {self.current_floor} to {target_floor}")
        yield self.env.timeout(travel_time)

        self.current_floor = target_floor
        self.moving = False
        print(f"[{self.env.now:.1f}] Elevator arrived at floor {self.current_floor}")

    def run(self):
        """
        Elevator main loop: process queued tasks in FIFO order.
        """
        while True:
            if self.task_queue:

              # Get next task
              next_floor = self.task_queue.popleft()
              print(f"[{self.env.now:.1f}] Elevator processing request to floor {next_floor}")

              # Move if necesary
              if next_floor == self.current_floor and not self.moving:
                print(f"[{self.env.now:.1f}] Elevator is already at floor {next_floor}")
              else:
                yield self.env.process(self.move_to(next_floor))
                yield self.env.process(self.hold(DEFAULT_WAIT_TIME)) # hold briefly after arrival
            else:

              # No tasks, execute resting policy:

              # 1. Stay at current floor
              # yield self.env.timeout(DEFAULT_CHECK_TIME)

              # 2. Go to base floor
              next_floor = self.base_floor

              if self.current_floor != next_floor:
                print(f"[{self.env.now:.1f}] Elevator vacant, going to floor {next_floor}")
                yield self.env.process(self.move_to(next_floor))

              yield self.env.timeout(DEFAULT_CHECK_TIME)