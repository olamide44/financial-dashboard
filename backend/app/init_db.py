from db import models  # noqa: E402
from db.database import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")