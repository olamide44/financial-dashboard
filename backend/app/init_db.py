# init_db.py  (sync)
from db import models                  # ensure models are imported/registered
from db.database import Base, engine   # regular Engine

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")