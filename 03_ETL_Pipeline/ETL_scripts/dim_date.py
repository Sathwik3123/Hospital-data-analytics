import os
import audit  # Updated audit.py for new logging
from datetime import datetime, timedelta
from connection import get_olap_conn

def load_date():
    """
    ETL process to populate the OLAP 'dim_date' dimension table.
    - Generates a date range from start_date to end_date.
    - Inserts dates with year, quarter, month, and day.
    - Row-level error handling and process-level logging included.
    """

    # ----------------------------
    # 1. Setup
    # ----------------------------
    file_name = os.path.basename(__file__)  # e.g., "dim_date.py"
    table_name = "dim_date"

    total_rows = 0
    rows_processed = 0
    rows_failed = 0

    # Establish connection to OLAP only
    conn = get_olap_conn()
    cursor = conn.cursor()

    try:
        # ----------------------------
        # 2. Define date range
        # ----------------------------
        start_date = datetime(2022, 1, 1)
        end_date = datetime(2026, 4, 30)
        curr = start_date

        # ----------------------------
        # 3. LOOP through date range
        # ----------------------------
        while curr <= end_date:
            total_rows += 1  # Count total dates to process
            try:
                dt_id = int(curr.strftime("%Y%m%d"))

                # Insert if not exists
                cursor.execute("""
                    INSERT INTO dim_date (id, full_date, year, quarter, month, day)
                    SELECT ?, ?, ?, ?, ?, ?
                    WHERE NOT EXISTS (
                        SELECT 1 FROM dim_date WHERE id = ?
                    )
                """, (
                    dt_id,
                    curr.date(),
                    curr.year,
                    (curr.month - 1) // 3 + 1,  # Quarter calculation
                    curr.month,
                    curr.day,
                    dt_id
                ))

                rows_processed += 1  # Successful insert

            except Exception as row_error:
                rows_failed += 1

                # Log row-level error
                audit.log_row_error(
                    file_name=file_name,
                    table_name=table_name,
                    failed_row_data=curr.strftime("%Y-%m-%d"),
                    error_message=str(row_error)
                )

            finally:
                # Move to next day
                curr += timedelta(days=1)

        # ----------------------------
        # 4. Commit all successful inserts
        # ----------------------------
        conn.commit()

        # ----------------------------
        # 5. Process-level logging
        # ----------------------------
        audit.log_etl_event(
            file_name=file_name,
            status="SUCESS",
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
        # 6. Cleanup connections
        # ----------------------------
        conn.close()