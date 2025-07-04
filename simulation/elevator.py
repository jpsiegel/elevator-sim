from datetime import timedelta
from collections import deque
import requests
import simpy
import math
import os

from params import DEFAULT_WAIT_TIME, DEFAULT_CHECK_TIME


class Elevator:
    def __init__(self, env: simpy.Environment, floors: tuple[int], speed_floors_per_sec: float, base_floor: int, simulation):
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
        self.simulation = simulation

        # Data structures
        self.last_snapshot = None # stores data of interest
        self.task_queue = deque()
        self.moving = False

        # Stats
        self.current_floor = base_floor
        self.last_floor = None
        self.idle_start_time = None
        self.request_histogram = {f: 0 for f in self.floors}

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
              self.idle_start_time = None
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

              if self.idle_start_time is None:
                self.idle_start_time = self.env.now
              
              # Here the elevator is vacant waiting for next requested floor,
              # so save a snapshot
              self.save_snapshot()

              yield self.env.timeout(DEFAULT_CHECK_TIME)

    def compute_mean_floor(self, histogram: dict):
        """
        Calculates the weighted mean floor based on cumulative demand histogram.
        Gives a notion of the location of a hot spot.
        """
        total = sum(histogram.values())
        if total == 0:
            return None  # or a default floor

        weighted_sum = sum(floor * count for floor, count in histogram.items())
        return weighted_sum / total
    

    def compute_center_of_mass_distance(self, current_floor: int):
        """
        Computes the absolute distance between the current floor and demand center of mass.
        Gives a notion of the distance to a hot spot.
        """
        mean = self.compute_mean_floor(self.request_histogram)
        if mean is None:
            return None

        return abs(current_floor - mean)
    
    def compute_entropy(self, histogram: dict):
        """
        Calculates the entropy of the cumulative floor demand histogram.
        Captures how predictable or chaotic the demand has been: 
        low entropy, requests come from few floors; 
        high entropy, requests evenly spread out.
        Gives a notion of the distribution we are dealing with and its predictability.

        Note: 0 ≤ entropy ≤ log2(floors)
        """
        total = sum(histogram.values())
        if total == 0:
            return None

        entropy = 0.0
        for count in histogram.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        return round(entropy, 3)


    def save_snapshot(self):
        """
        Captures elevator state when idle and relevant features.
        Stores the data with expected backend format, but in memory to add label later.
        """
        timestamp = self.simulation.start_datetime + timedelta(seconds=self.env.now)

        # Features to compute
        histogram = [self.request_histogram[f] for f in self.floors]
        entropy = self.compute_entropy(self.request_histogram)
        #hot_floor = self.get_hot_floor_last_30s() # TODO
        mean_floor = self.compute_mean_floor(self.request_histogram)
        center_of_mass_distance = self.compute_center_of_mass_distance(self.current_floor)

        # Create dict as expected by backend
        self.last_snapshot = {
            "simulation_id": self.simulation.simulation_id,
            "current_floor": self.current_floor,
            "last_floor": self.last_floor,
            "time_idle": round(self.env.now - self.idle_start_time, 3),
            "timestamp": timestamp.isoformat(),
            "floor_demand_histogram": histogram,
            #"hot_floor_last_30s": hot_floor, # TODO
            "requests_entropy": entropy,
            "mean_requested_floor": mean_floor,
            "distance_to_center_of_mass": center_of_mass_distance,
            "next_floor_requested": None
        }
        print("snapshot created", self.last_snapshot)

    def post_snapshot(self):
        """
        Stores the completed snapshot in the backend database.

        Example snapshot:
        {
        'simulation_id': 13,
        'current_floor': 1, 
        'last_floor': 2, 
        'time_idle': 52.0, 
        'timestamp': '2025-07-04T18:55:18.39', 
        'floor_demand_histogram': [2, 1, 1, 1, 0], 
        'requests_entropy': 1.922, 
        'mean_requested_floor': 2.2, 
        'distance_to_center_of_mass': 1.20, 
        'next_floor_requested': 3
        }
        """
        if not self.last_snapshot:
            raise ValueError("No snapshot to store!")

        # api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        # endpoint = f"{api_url}/elevator_request"
        # response = requests.post(endpoint, json=self.last_snapshot)

        # if response.status_code != 200:
        #     raise Exception(f"Failed to post elevator request: {response.status_code} {response.text}")
        print(f"[{self.env.now:.1f}] Snapshot posted: {self.last_snapshot}")


