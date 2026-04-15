import os
import logging
import psycopg2
from dotenv import load_dotenv

# Configure logging for professional status tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def get_connection():
    """
    Establishes a connection to the PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
        return connection
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Connection failed: {error}")
        return None

def create_tables():
    """
    Creates multiple relational tables in the database
    following the exact requirements from the Neon tutorial.
    """
    # 1. Define the SQL commands as a tuple
    commands = (
        """
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id SERIAL PRIMARY KEY,
            vendor_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS parts (
            part_id SERIAL PRIMARY KEY,
            part_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS part_drawings (
            part_id INTEGER PRIMARY KEY,
            file_extension VARCHAR(5) NOT NULL,
            drawing_data BYTEA NOT NULL,
            FOREIGN KEY (part_id) REFERENCES parts (part_id) 
            ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS vendor_parts (
            vendor_id INTEGER NOT NULL,
            part_id INTEGER NOT NULL,
            PRIMARY KEY (vendor_id , part_id),
            FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id) 
                ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (part_id) REFERENCES parts (part_id) 
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """
    )
    
    conn = get_connection()
    if conn:
        try:
            # 2. Create a cursor to execute SQL commands
            with conn.cursor() as cur:
                # 3. Loop through the tuple and execute each command
                for command in commands:
                    cur.execute(command)
                
                # 4. Commit the changes to the database once all tables are executed
                conn.commit()
                logger.info("--- [SUCCESS] All 4 relational tables created successfully! ---")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Failed to create tables: {error}")
        finally:
            # 5. Always close the connection
            conn.close()
            logger.info("--- Connection closed safely. ---")

if __name__ == "__main__":
    # Execute the table creation logic
    create_tables()