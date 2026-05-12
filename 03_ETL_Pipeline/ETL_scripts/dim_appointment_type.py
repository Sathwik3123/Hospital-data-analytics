
import os
import audit  # Updated audit.py for new logging
from connection import get_oltp_conn, get_olap_conn

def load_appointment_type():
    """
    ETL process to load data from OLTP 'appointment_type' table
    into OLAP 'dim_appointment_type' dimension table.
    
    Features:
    - Row-level error handling with detailed logging
    - Process-level logging with counts of total, processed, failed rows
    - Dynamic ETL file tracking using file_name
    """

    # ----------------------------
    # 1. Setup
    # ----------------------------
    file_name = os.path.basename(__file__)  # e.g., "dim_appointment_type.py"
    table_name = "dim_appointment_type"

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
        # 2. EXTRACT from OLTP
        # ----------------------------
        oc.execute("SELECT id, name,  base_charge FROM appointment_type")
        rows = oc.fetchall()
        total_rows = len(rows)  # Track total rows fetched

        # ----------------------------
        # 3. LOAD into OLAP with row-level error handling
        # ----------------------------
        for r in rows:
            try:
                ac.execute("""
                    INSERT INTO dim_appointment_type 
                    (appointment_type_id, appointment_name, base_charge) 
                    VALUES (?, ?, ?)
                """, r)

                rows_processed += 1  # Successful insert counter

            except Exception as row_error:
                rows_failed += 1  # Failed insert counter

                # Log individual row errors
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


