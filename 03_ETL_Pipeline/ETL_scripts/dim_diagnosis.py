import os
import audit
from connection import get_oltp_conn, get_olap_conn

def load_diagnosis():
    """
    ETL process to load diagnosis data from OLTP into OLAP 'dim_diagnosis' dimension table.

    Features:
    - Row-level error handling with detailed logging
    - Process-level logging with counts of total, processed, failed rows
    - Dynamic ETL file tracking using file_name
    """

    # ----------------------------
    # 1. Setup
    # ----------------------------
    file_name = os.path.basename(__file__)   # e.g., "dim_diagnosis.py"
    table_name = "dim_diagnosis"

    total_rows = 0
    rows_processed = 0
    rows_failed = 0

    # Establish connections
    oltp = get_oltp_conn()   # OLTP source
    olap = get_olap_conn()   # OLAP destination
    oc = oltp.cursor()
    ac = olap.cursor()

    try:
        # ----------------------------
        # 2. EXTRACT: fetch diagnosis data
        # ----------------------------
        oc.execute("""
            SELECT 
                id,
                icd10_code,
                name,
                is_chronic
            FROM diagnosis
        """)

        rows = oc.fetchall()
        total_rows = len(rows)

        # ----------------------------
        # 3. LOAD: insert into OLAP
        # ----------------------------
        for r in rows:
            try:
                ac.execute("""
                    INSERT INTO dim_diagnosis
                    (diagnosis_id, icd_10_code, diagnosis_name, is_chronic)
                    VALUES (?, ?, ?, ?)
                """, r)

                rows_processed += 1

            except Exception as row_error:
                rows_failed += 1

                audit.log_row_error(
                    file_name=file_name,
                    table_name=table_name,
                    failed_row_data=r,
                    error_message=str(row_error)
                )

                continue

        # Commit successful inserts
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