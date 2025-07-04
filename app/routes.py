from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models import SimulationMetadata, ElevatorRequest
from schemas import SimulationCreate, SimulationOut, ElevatorRequestCreate, ElevatorRequestOut
from db import get_db

router = APIRouter()

# Simulation endpoints ---

@router.post("/simulation", response_model=SimulationOut)
def create_simulation(sim_data: SimulationCreate, db: Session = Depends(get_db)):
  """
  Create a single simulation object
  """
  sim = SimulationMetadata(**sim_data.dict())
  db.add(sim)
  db.commit()
  db.refresh(sim)
  return sim


@router.get("/simulations", response_model=List[SimulationOut])
def get_simulations(db: Session = Depends(get_db)):
  """
  Read all available simulations 
  """
  return db.query(SimulationMetadata).all()


@router.get("/simulation/{id}", response_model=SimulationOut)
def get_simulation(id: int, db: Session = Depends(get_db)):
  """
  Read a specific simulation
  """
  sim = db.query(SimulationMetadata).filter(SimulationMetadata.id == id).first()
  if not sim:
      raise HTTPException(status_code=404, detail="Simulation not found")
  return sim


# Requests endpoints ---

@router.post("/elevator_request", response_model=ElevatorRequestOut)
def create_elevator_request(req_data: ElevatorRequestCreate, db: Session = Depends(get_db)):
  """
  Creates a single request
  """
  req = ElevatorRequest(**req_data.dict())
  db.add(req)
  db.commit()
  db.refresh(req)
  return req


@router.get("/elevator_request/{sim_id}", response_model=List[ElevatorRequestOut])
def get_requests_for_simulation(sim_id: int, db: Session = Depends(get_db)):
  """
  Read all requests that correspond to a specific simulation
  """
  return db.query(ElevatorRequest).filter(ElevatorRequest.simulation_id == sim_id).all()
