from datetime import timedelta
from collections import deque
import requests
import simpy
import os

from params import DEFAULT_WAIT_TIME, DEFAULT_CHECK_TIME


class Elevator:
    def __init__(self, env: simpy.Environment, floors: tuple[int], speed_floors_per_sec: float, base_floor: int):
        """
        Elevator agent, takes requests and moves across floors and stores data of interest.

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

        self.last_snapshot = None # stores data of interest
        self.current_floor = base_floor
        self.task_queue = deque()
        self.moving = False
        self.last_floor = None

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
        self.last_floor = self.current_floor

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

              # 3. Use prediction from a model
              # WIP

              # Here the elevator is vacant waiting for next requested floor,
              # so save a snapshot
              self.save_snapshot()

              yield self.env.timeout(DEFAULT_CHECK_TIME)

    def save_snapshot(self):
        """
        Captures elevator state when idle and relevant features.
        Stores the data with expected backend format, but in memory to add label later.
        """
        #timestamp = self.start_datetime + timedelta(seconds=self.env.now)

        # Features to compute
        #histogram = self.get_floor_demand_histogram()
        #entropy = self.compute_entropy(histogram)
        #hot_floor = self.get_hot_floor_last_30s()
        #mean_floor = self.compute_mean_floor(histogram)
        #center_of_mass = self.compute_center_of_mass_distance(self.current_floor, histogram)

        # Create dict as expected by backend
        self.last_snapshot = {
            #"simulation_id": self.simulation_id,
            "current_floor": self.current_floor,
            "last_floor": self.last_floor,
            #"time_idle": time_idle,
            #"timestamp": timestamp.isoformat(),
            #"floor_demand_histogram": histogram,
            #"hot_floor_last_30s": hot_floor,
            #"requests_entropy": entropy,
            #"mean_requested_floor": mean_floor,
            #"distance_to_center_of_mass": center_of_mass,
            "next_floor_requested": None
        }
        print("snapshot created", self.last_snapshot)

    def post_snapshot(self):
        """
        Stores the completed snapshot in the backend database.
        """
        if not self.last_snapshot:
            raise ValueError("No snapshot to store!")

        # api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        # endpoint = f"{api_url}/elevator_request"
        # response = requests.post(endpoint, json=self.last_snapshot)

        # if response.status_code != 200:
        #     raise Exception(f"Failed to post elevator request: {response.status_code} {response.text}")
        print(f"[{self.env.now:.1f}] Snapshot posted: {self.last_snapshot}")


