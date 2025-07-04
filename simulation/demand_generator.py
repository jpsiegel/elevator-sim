from typing import Tuple
import simpy
import random

from params import BASE_FLOOR_WEIGHT

class DemandGenerator:
    def __init__(self, env: simpy.Environment, floors: tuple[int], elevator, lambda_: float):
        """
        Generates elevator demand at random intervals.

        Args:
            env: SimPy environment
            floors: Valid floor numbers
            elevator: Reference to the Elevator instance
            lambda_: Mean arrival interval (Exponential distribution)
        """
        self.env = env
        self.floors = floors
        self.elevator = elevator
        self.lambda_ = lambda_

        # Start the generator process
        self.process = env.process(self.run())

    def generate_interarrival_time(self) -> float:
        """
        Samples the next interarrival time from an exponential distribution.
        """
        return random.expovariate(self.lambda_)

    def generate_origin_destination(self) -> Tuple[int, int]:
        """
        Selects origin and destination floors from a distribution.
        Ensures origin != destination.
        """
        origin = self.weighted_floor_choice()
        destination = self.weighted_floor_choice(exclude=origin)
        return origin, destination

    def weighted_floor_choice(self, exclude: int = None) -> int:
        """
        Selects a floor with higher probability for base floor.
        Optionally excludes a specific floor.
        This mimics a uniform distribution with a peak.
        """
        valid_floors = [floor for floor in self.floors if floor != exclude]
        weights = [BASE_FLOOR_WEIGHT if floor == self.elevator.base_floor else 1 for floor in valid_floors]
        return random.choices(valid_floors, weights=weights, k=1)[0]

    def run(self):
        """
        Generates demand at stochastic intervals and sends tasks to the elevator.
        """
        while True:
            # Wait until next demand
            interarrival_time = self.generate_interarrival_time()
            yield self.env.timeout(interarrival_time)

            # Generate a random request
            origin, destination = self.generate_origin_destination()

            # We have label for the snapshot (next request), update, store and clean
            if self.elevator.last_snapshot:
                self.elevator.last_snapshot["next_floor_requested"] = origin
                self.elevator.post_snapshot()
                self.elevator.last_snapshot = None


            # Elevator gets a task to go to origin then to destination
            print(f"[{self.env.now:.1f}] Request: from {origin} to {destination}")
            self.elevator.add_task(origin)
            self.elevator.add_task(destination)