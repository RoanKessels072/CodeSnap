from database.db import engine, Base
from models.user import User
from models.exercise import Exercise
from models.attempt import Attempt

Base.metadata.drop_all(bind=engine)

Base.metadata.create_all(bind=engine)