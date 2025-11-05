from database.db import get_engine, Base
from models.user import User
from models.exercise import Exercise
from models.attempt import Attempt

Base.metadata.drop_all(bind=get_engine)

Base.metadata.create_all(bind=get_engine)