from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SimulationMetadata(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)

    # Simulation parameters
    wait_time = Column(Float, nullable=False)  # seconds
    elevator_speed = Column(Float, nullable=False)  # floors/sec
    expo_lambda = Column(Float, nullable=False) # req/sec
    duration = Column(Integer, nullable=False)  # seconds
    base_floor = Column(Integer, nullable=True)
    base_floor_weight = Column(Float, nullable=True) # chance multiplier
    floor_min = Column(Integer, nullable=False)
    floor_max = Column(Integer, nullable=False)
    random_seed = Column(Integer, nullable=False) # for reproducibility

    # 1-N relationship with requests
    requests = relationship("ElevatorRequest", back_populates="simulation")


class ElevatorRequest(Base):
    __tablename__ = "elevator_requests"

    id = Column(Integer, primary_key=True, index=True)

    # N-1 relationship with simulation
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False)
    simulation = relationship("SimulationMetadata", back_populates="requests")
