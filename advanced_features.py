import os
import logging
import psycopg2
from database import get_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_database_routines():
    """
    Injects the necessary Function and Procedure into Postgres 
    so we can test them via Python later.
    """
    create_function_sql = """
    CREATE OR REPLACE FUNCTION get_parts_by_vendor(id integer)
    RETURNS TABLE(part_id INTEGER, part_name VARCHAR) AS $$
    BEGIN
        RETURN QUERY
        SELECT parts.part_id, parts.part_name
        FROM parts
        INNER JOIN vendor_parts ON vendor_parts.part_id = parts.part_id
        WHERE vendor_id = id;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    create_procedure_sql = """
    CREATE OR REPLACE PROCEDURE add_new_part(new_part_name VARCHAR, new_vendor_name VARCHAR)
    LANGUAGE plpgsql AS $$
    DECLARE
        v_part_id INTEGER;
        v_vendor_id INTEGER;
    BEGIN
        INSERT INTO parts(part_name) VALUES(new_part_name) RETURNING part_id INTO v_part_id;
        INSERT INTO vendors(vendor_name) VALUES(new_vendor_name) RETURNING vendor_id INTO v_vendor_id;
        INSERT INTO vendor_parts(part_id, vendor_id) VALUES(v_part_id, v_vendor_id);
    END;
    $$;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_function_sql)
            cur.execute(create_procedure_sql)
            conn.commit()
            logger.info("Setup: Injected Function and Procedure into Database.")

def call_function_get_parts(vendor_id):
    """
    Link 5: Call a PostgreSQL Function that returns data using callproc().
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # callproc takes the function name and a tuple of arguments
            cur.callproc('get_parts_by_vendor', (vendor_id,))
            rows = cur.fetchall()
            logger.info(f"--- Parts for Vendor {vendor_id} ---")
            for row in rows:
                logger.info(f"Part ID: {row[0]}, Part Name: {row[1]}")

def call_procedure_add_part(part_name, vendor_name):
    """
    Link 6: Call a PostgreSQL Stored Procedure (does not return data).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Procedures are called using the CALL SQL command
            cur.execute("CALL add_new_part(%s, %s);", (part_name, vendor_name))
            conn.commit()
            logger.info(f"Procedure executed: Added part '{part_name}' and vendor '{vendor_name}'.")

def write_blob(part_id, file_path, file_extension):
    """
    Link 7: Read a physical file and save it to the database as a BLOB (BYTEA).
    """
    try:
        # Read the file as binary
        with open(file_path, 'rb') as file:
            drawing_data = file.read()
            
        query = """
        INSERT INTO part_drawings (part_id, file_extension, drawing_data)
        VALUES (%s, %s, %s)
        ON CONFLICT (part_id) DO UPDATE SET drawing_data = EXCLUDED.drawing_data;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                # psycopg2.Binary safely wraps the binary data
                cur.execute(query, (part_id, file_extension, psycopg2.Binary(drawing_data)))
                conn.commit()
                logger.info(f"BLOB saved: Wrote {file_path} to Database for part_id {part_id}")
    except FileNotFoundError:
        logger.error(f"Could not find file {file_path}. Please create a dummy file to test BLOBs.")

if __name__ == "__main__":
    setup_database_routines()
    
    # Test Procedure (Link 6)
    call_procedure_add_part("OLED Screen", "Samsung Displays")
    
    # Test Function (Link 5)
    # The procedure above inserts a new vendor, let's query its parts. 
    # (Assuming it gets ID 5 based on previous runs, adjust if necessary)
    call_function_get_parts(5)
    
    # Test BLOB (Link 7)
    # create a dummy text file to act as our 'drawing'
    with open('dummy_drawing.txt', 'w') as f:
        f.write("This is a fake engineering drawing data.")
        
    write_blob(part_id=1, file_path='dummy_drawing.txt', file_extension='txt')