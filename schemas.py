from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Simulation schema ---

class SimulationBase(BaseModel):
    wait_time: float
    elevator_speed: float
    expo_lambda: float
    start_datetime: datetime
    duration: int
    base_floor: Optional[int] = None
    base_floor_weight: Optional[float] = None
    floor_min: int
    floor_max: int
    random_seed: int

class SimulationCreate(SimulationBase):
    pass

class SimulationOut(SimulationBase):
    id: int
    class Config:
        orm_mode = True


# Request schema ---

class ElevatorRequestBase(BaseModel):
    current_floor: int
    last_floor: int
    time_idle: float
    timestamp: datetime
    floor_demand_histogram: List[int]
    hot_floor_last_30s: Optional[int] = None
    requests_entropy: Optional[float] = None
    mean_requested_floor: Optional[float] = None
    distance_to_center_of_mass: Optional[float] = None
    next_floor_requested: Optional[int] = None

class ElevatorRequestCreate(ElevatorRequestBase):
    simulation_id: int

class ElevatorRequestOut(ElevatorRequestBase):
    id: int
    simulation_id: int

    class Config:
        orm_mode = True
