

import os
import audit  # Updated audit.py for new logging
from connection import get_oltp_conn, get_olap_conn

def load_visit_type():
    """
    ETL process to load visit type data from OLTP into OLAP 'dim_visit_type' dimension table.

    Features:
    - Row-level error handling with detailed logging
    - Process-level logging with counts of total, processed, failed rows
    - Dynamic ETL file tracking using file_name
    """

    # ----------------------------
    # 1. Setup
    # ----------------------------
    file_name = os.path.basename(__file__)  # e.g., "dim_visit_type.py"
    table_name = "dim_visit_type"

    total_rows = 0
    rows_processed = 0
    rows_failed = 0

    # Establish connections
    oltp = get_oltp_conn()  # OLTP source
    olap = get_olap_conn()  # OLAP destination
    oc = oltp.cursor()
    ac = olap.cursor()

    try:
        # ----------------------------
        # 2. EXTRACT: fetch visit types
        # ----------------------------
        oc.execute("SELECT id, name FROM visit_type")
        rows = oc.fetchall()
        total_rows = len(rows)  # Track total rows fetched

        # ----------------------------
        # 3. LOAD: insert into OLAP with row-level error handling
        # ----------------------------
        for r in rows:
            try:
                ac.execute("""
                    INSERT INTO dim_visit_type
                    (visit_type_id, visit_type_name)
                    VALUES (?, ?)
                """, r)

                rows_processed += 1  # Successful insert counter

            except Exception as row_error:
                rows_failed += 1  # Failed insert counter

                # Log row-level failure
                audit.log_row_error(
                    file_name=file_name,
                    table_name=table_name,
                    failed_row_data=r,
                    error_message=str(row_error)
                )

                continue  # Skip bad row and continue

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
        # Major ETL failure (connection/query issues)
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