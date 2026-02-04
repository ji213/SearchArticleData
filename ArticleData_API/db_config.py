import os
from dotenv import load_dotenv


DOTENV_FILE_PATH = ".env"


def get_db_connection_string():
    """
    Loads database credentials from .env and returns a 
    formatted pyodbc connection string.
    """
    # Load the .env file
    load_dotenv(DOTENV_FILE_PATH)

    # Retrieve variables
    driver = os.getenv("DRIVER")
    server = os.getenv("SERVER_NAME")
    database = os.getenv("DATABASE_NAME")

    # Validation: Ensure all required fields exist
    if not all([driver, server, database]):
        missing = [k for k, v in {"DRIVER": driver, "SERVER": server, "DATABASE": database}.items() if not v]
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    # Construct the string
    connection_string = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )
    
    return connection_string