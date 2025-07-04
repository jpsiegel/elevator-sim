from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SimulationMetadata(Base):
    """
    Stores data describing the simulation, each simulation has many requets.
    Parameters can be used to reproduce a simulation or provide extra features.
    """
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)

    # Simulation parameters
    wait_time = Column(Float, nullable=False)  # seconds
    elevator_speed = Column(Float, nullable=False)  # floors/sec
    expo_lambda = Column(Float, nullable=False)  # req/sec
    start_datetime = Column(DateTime, nullable=False) # Timestamp
    duration = Column(Integer, nullable=False)  # seconds
    base_floor = Column(Integer, nullable=True)
    base_floor_weight = Column(Float, nullable=True)  # chance multiplier
    floor_min = Column(Integer, nullable=False)
    floor_max = Column(Integer, nullable=False)
    random_seed = Column(Integer, nullable=False)  # for reproducibility

    # 1-N relationship with requests
    requests = relationship("ElevatorRequest", back_populates="simulation")


class ElevatorRequest(Base):
    """
    Snapshot of the simulation when the elevator was idle waiting for next requested floor.
    Used as features to train a model, next_floor_requested can be sused as label.
    Each record belongs to a single simulation.
    """
    __tablename__ = "elevator_requests"

    id = Column(Integer, primary_key=True, index=True)

    # State features
    current_floor = Column(Integer, nullable=False)
    last_floor = Column(Integer, nullable=False)
    time_idle = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Calculated indicators
    floor_demand_histogram = Column(ARRAY(Integer), nullable=False)  # eg: [1, 2, 0, 3, 1]
    hot_floor_last_30s = Column(Integer, nullable=True)
    requests_entropy = Column(Float, nullable=True)
    mean_requested_floor = Column(Float, nullable=True)
    distance_to_center_of_mass = Column(Float, nullable=True)

    # Label
    next_floor_requested = Column(Integer, nullable=True)

    # N-1 relationship with simulation
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    simulation = relationship("SimulationMetadata", back_populates="requests")
