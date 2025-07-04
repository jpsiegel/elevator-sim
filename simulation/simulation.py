import simpy
from datetime import datetime, timedelta

from elevator import Elevator
from demand_generator import DemandGenerator

from params import (
    SIMULATION_DURATION,
    FLOORS, DEFAULT_SPEED,
    DEFAULT_LAMBDA, DEFAULT_BASE_FLOOR
)

class Simulation:
    def __init__(
        self,
        sim_time: float,
        floors: tuple[int],
        speed_floors_per_sec: float,
        lambda_: float,
        base_floor: int,
        start_datetime: datetime
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

if __name__ == "__main__":
    sim = Simulation(
        sim_time=SIMULATION_DURATION,
        floors=FLOORS,
        speed_floors_per_sec=DEFAULT_SPEED,
        lambda_=DEFAULT_LAMBDA,
        base_floor=DEFAULT_BASE_FLOOR,
        start_datetime=datetime.now()
    )
    print("Simulation started at:", sim.start_datetime)
    sim.run()
    print("Simulation ended at:", sim.start_datetime + timedelta(seconds=sim.sim_time))