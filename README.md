# Elevator Simulation

## Overview
This software system is used to create high quality synthetic data and store it to be used in a ML ingestion pipeline.
The design considers 3 main components:
- Simulation
- API
- Database

### Simulation
A descrete event simulation in simpy is proposed to model the elevator scenario, its a great tool for logistics and phenomena that follows Poisson processes.
This allows us to recreate an environment where the elevator can perform its actions realistically and add all the logic we want.
For this case a simple simulation was created, considering a single elevator in a building with n floors, the requests are taken and executed in FIFO order.
A bit of business logic was added, considering that the first floor is usually at street level and is much busier, a spike in the demand for floor one was added, also, the elevator rests at the first floor when idle. 
The generated data is posted to the API at runtime.

### API
A simple FastAPI was developed, with endpoint to create and read generated data. See routes.py
These allow the simulation to store data in the database, and the future ML pipeline to retrieve this data to train.
Also, tests were added to check the endpoints functionality.

### Database
A FastAPI data model connected to a PostgreSQL data schema is proposed (see models.py) to store simulation metadata and labeled demand data.
We store a snapshot of the state of the simulation when a relevant demand was created (features) and then add the next requested floor created after that scenario (label).
Also, a simple test was added to check the database connection with the API.

#### Note
The system was designed in a containerized fashion, to be able to deploy it easily in a production environment (see docker-compose.yml).
The logic was separated as a different service for the simulations and for the app, since the simulation could be very resource heavy and we dont want to overload the backend.
