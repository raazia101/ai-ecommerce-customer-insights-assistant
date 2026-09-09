import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
database = os.getenv("POSTGRES_DB")

url = (
    f"postgresql+psycopg://{user}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(url)

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT current_database(), current_user")
    )
    print(result.fetchone())