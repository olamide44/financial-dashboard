from db import models  # noqa: E402
from db.database import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)