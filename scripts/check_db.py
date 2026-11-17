from sqlalchemy import text

from app.db import engine

with engine.connect() as connection:
    print(connection.execute(text("SELECT version()")).scalar_one())
    print(connection.execute(text("SELECT extname FROM pg_extension WHERE extname = 'pg_trgm'")).scalar_one_or_none())