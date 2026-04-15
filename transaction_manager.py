import logging
import psycopg2
from database import get_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def assign_part_to_vendor(vendor_id, part_name):
    """
    Link 4: Transaction Handling.
    We must insert a new part AND link it to a vendor. 
    If linking fails, the new part insertion MUST be rolled back.
    """
    insert_part_query = "INSERT INTO parts(part_name) VALUES(%s) RETURNING part_id;"
    assign_vendor_query = "INSERT INTO vendor_parts(vendor_id, part_id) VALUES(%s, %s);"
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # 1. Insert the new part
            cur.execute(insert_part_query, (part_name,))
            part_id = cur.fetchone()[0]
            logger.info(f"Part '{part_name}' inserted with ID: {part_id}")
            
            # 2. Link it to the vendor
            cur.execute(assign_vendor_query, (vendor_id, part_id))
            logger.info(f"Part '{part_name}' assigned to Vendor ID: {vendor_id}")
            
            # 3. Commit only if BOTH operations succeed
            conn.commit()
            logger.info("Transaction committed successfully.")
            
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Transaction failed. Rolling back changes. Error: {error}")
        if conn is not None:
            # Revert all changes in this block
            conn.rollback()
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    # Assuming vendor ID 1 exists from our previous CRUD tests
    assign_part_to_vendor(1, "Antenna")
    
    # Intentionally failing transaction (Vendor ID 9999 doesn't exist -> Foreign Key Error)
    # This will trigger the rollback mechanism!
    logger.info("--- Testing Rollback Mechanism ---")
    assign_part_to_vendor(9999, "Corrupted Part")