from datetime import datetime, timedelta
import simpy
import random
import os
import requests

from elevator import Elevator
from demand_generator import DemandGenerator

from params import (
    SIMULATION_DURATION,
    FLOORS, DEFAULT_SPEED,
    DEFAULT_LAMBDA, 
    DEFAULT_BASE_FLOOR,
    DEFAULT_WAIT_TIME, 
    BASE_FLOOR_WEIGHT,
)

class Simulation:
    def __init__(
        self,
        sim_time: float,
        floors: tuple[int],
        speed_floors_per_sec: float,
        lambda_: float,
        base_floor: int,
        start_datetime: datetime,
        seed: int
    ):
        """
        Main simulation controller.

        Args:
            sim_time: Total duration of the simulation (in seconds)
            floors: Valid floor numbers (e.g., (1, 2, ..., 10))
            speed_floors_per_sec: Elevator travel speed
            lambda_: Average time between user requests (Poisson process)
            base_floor: Starting floor
        """
        self.sim_time = sim_time
        self.env = simpy.Environment()
        self.start_datetime = start_datetime
        self.simulation_id = None # is set by backend

        # Set seed
        self.seed = seed
        random.seed(seed)

        # Initialize elevator and demand generator
        self.elevator = Elevator(
            env=self.env,
            floors=floors,
            speed_floors_per_sec=speed_floors_per_sec,
            base_floor=base_floor
        )

        self.demand_generator = DemandGenerator(
            env=self.env,
            floors=floors,
            elevator=self.elevator,
            lambda_=lambda_
        )

    def run(self):
        """
        Runs the simulation.
        """
        self.env.run(until=self.sim_time)

    def post_metadata(self):
        """
        Sends simulation metadata to the FastAPI backend.
        Returns the simulation ID assigned by the API.
        """
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        endpoint = f"{api_url}/simulation"

        payload = {
            "wait_time": DEFAULT_WAIT_TIME,
            "elevator_speed": self.elevator.speed,
            "expo_lambda": self.demand_generator.lambda_,
            "start_datetime": self.start_datetime.isoformat(),
            "duration": int(self.sim_time),
            "base_floor": self.elevator.base_floor,
            "base_floor_weight": BASE_FLOOR_WEIGHT,
            "floor_min": min(self.elevator.floors),
            "floor_max": max(self.elevator.floors),
            "random_seed": self.seed,
        }

        response = requests.post(endpoint, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to post simulation metadata: {response.status_code} {response.text}")

        sim_data = response.json()
        print(f"Simulation metadata saved with ID: {sim_data['id']}")
        self.simulation_id = sim_data["id"]

if __name__ == "__main__":
    sim = Simulation(
        sim_time=SIMULATION_DURATION,
        floors=FLOORS,
        speed_floors_per_sec=DEFAULT_SPEED,
        lambda_=DEFAULT_LAMBDA,
        base_floor=DEFAULT_BASE_FLOOR,
        start_datetime=datetime.now(),
        seed=31
    )
    print("Simulation started at:", sim.start_datetime)
    sim.post_metadata() # save metadata before starting
    sim.run()
    print("Simulation ended at:", sim.start_datetime + timedelta(seconds=sim.sim_time))