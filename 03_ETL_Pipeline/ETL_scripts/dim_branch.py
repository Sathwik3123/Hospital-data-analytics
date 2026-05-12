import os
import audit  # Updated audit.py for new logging
from connection import get_oltp_conn, get_olap_conn

def load_branch():
    """
    ETL process to load hierarchical branch data from OLTP (state → city → hospital_branch)
    into OLAP 'dim_branch' dimension table.
    
    Features:
    - Row-level error handling with detailed logging
    - Process-level logging with total, processed, failed rows
    - Dynamic ETL file tracking using file_name
    """

    # ----------------------------
    # 1. Setup
    # ----------------------------
    file_name = os.path.basename(__file__)  # e.g., "dim_branch.py"
    table_name = "dim_branch"

    total_rows = 0
    rows_processed = 0
    rows_failed = 0

    # Establish database connections
    oltp = get_oltp_conn()  # OLTP source
    olap = get_olap_conn()  # OLAP destination
    oc = oltp.cursor()
    ac = olap.cursor()

    try:
        # ----------------------------
        # 2. EXTRACT: Fetch branch hierarchy
        # ----------------------------
        query = """
            SELECT s.id, s.name, c.id, c.name, b.id, b.name,c.longitude,c.latitude
            FROM state s
            JOIN city c ON s.id = c.state_id
            JOIN hospital_branch b ON c.id = b.city_id
        """
        oc.execute(query)
        rows = oc.fetchall()
        total_rows = len(rows)  # Track total rows fetched

        # ----------------------------
        # 3. LOAD: Insert into OLAP with row-level error handling
        # ----------------------------
        for r in rows:
            try:
                ac.execute("""
                    INSERT INTO dim_branch 
                    (state_id, state_name, city_id, city_name, branch_id, branch_name,longitude,latitude)
                    VALUES (?, ?, ?, ?, ?, ?,?,?)
                """, r)

                rows_processed += 1  # Count successful inserts

            except Exception as row_error:
                rows_failed += 1

                # Log row-level failure
                audit.log_row_error(
                    file_name=file_name,
                    table_name=table_name,
                    failed_row_data=r,
                    error_message=str(row_error)
                )

                continue  # Skip failed row and continue

        # Commit all successful inserts
        olap.commit()

        # ----------------------------
        # 4. Process-level logging
        # ----------------------------

        if total_rows>0 and rows_processed==0:
            status="DATA_ERROR"
        elif rows_failed>0:
            status="PARTIAL_SUCCESS"  
        else:
            status="SUCCESS" 
        
        audit.log_etl_event(
            file_name=file_name,
            status=status,
            total_rows=total_rows,
            rows_processed=rows_processed,
            rows_failed=rows_failed
        )



    except Exception as e:
        # Major ETL failure (e.g., connection issues)
        audit.log_etl_event(
            file_name=file_name,
            status="EXECUTION_FAILED",
            total_rows=total_rows,
            rows_processed=rows_processed,
            rows_failed=rows_failed
        )

    finally:
        # ----------------------------
        # 5. Cleanup connections
        # ----------------------------
        oltp.close()
        olap.close()