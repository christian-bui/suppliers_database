import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


def get_connection():
    """
    Establishes a connection to the PostgreSQL database using environment variables.

    Returns:
        psycopg2.extensions.connection: The database connection object or None if failed.
    """
    try:
        # Fetch credentials from environment variables
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
        print("--- [SUCCESS] Connected to PostgreSQL successfully! ---")
        return connection
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"--- [ERROR] Connection failed: {error} ---")
        return None


if __name__ == "__main__":
    # Test the database connection
    conn = get_connection()
    if conn:
        conn.close()
        print("--- Connection closed safely. ---")
