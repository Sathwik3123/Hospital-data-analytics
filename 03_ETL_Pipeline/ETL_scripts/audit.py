


from connection import get_olap_conn
from datetime import datetime


# ----------------------------
# PROCESS LEVEL LOGGING
# ----------------------------
def log_etl_event(file_name, status, total_rows=0, rows_processed=0, rows_failed=0):
    conn = get_olap_conn()
    cursor = conn.cursor()

    query = """
        INSERT INTO etl_log 
        (file_name, execution_date, status, total_rows, rows_processed, rows_failed)
        VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(query, (
        file_name,                 # example: "fact_billing_loader.py"
        datetime.now(),
        status,                    # SUCCESS / FAILED 
        total_rows,
        rows_processed,
        rows_failed
    ))

    conn.commit()
    conn.close()


# ----------------------------
# ROW LEVEL ERROR LOGGING
# ----------------------------
def log_row_error(file_name, table_name, failed_row_data, error_message):
    conn = get_olap_conn()
    cursor = conn.cursor()

    query = """
        INSERT INTO log_row_error
        (file_name, table_name, execution_date, failed_rows_data, error_message)
        VALUES (?, ?, ?, ?, ?)
    """

    cursor.execute(query, (
        file_name,                     # example: "fact_billing_loader.py"
        table_name,                    # example: "fact_billing"
        datetime.now(),
        str(failed_row_data),
        str(error_message)
    ))

    conn.commit()
    conn.close()