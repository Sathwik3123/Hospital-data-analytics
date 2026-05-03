

import os
import audit  # Updated audit.py for new logging
from connection import get_oltp_conn, get_olap_conn

def load_fact_visit():
    """
    ETL process to load patient visit data from OLTP into OLAP 'fact_visit' fact table.
    Updated to include diagnosis_key and patient rating.
    """

    # ----------------------------
    # 1. Setup
    # ----------------------------
    file_name = os.path.basename(__file__)
    table_name = "fact_visit"

    total_rows = 0
    rows_processed = 0
    rows_failed = 0

    # Establish connections
    oltp = get_oltp_conn()
    olap = get_olap_conn()
    oc = oltp.cursor()
    ac = olap.cursor()

    try:
        # ----------------------------
        # 2. EXTRACT: Updated query with diagnosis and rating
        # ----------------------------
        query = """
           
            SELECT 
                do.id AS date_key,
                dv.id AS visit_type_key,
                dd.id AS doctor_key,
                dp.id AS patient_key,
                da.id AS appointment_type_key,
                db.id AS branch_key,
                dt.id AS treatment_key,
                dg.id AS diagnosis_key,
                do1.id as discharge_date,
                df.rating AS rating
            FROM [medical_oltp].dbo.patient_visit pv
            INNER JOIN [medical_database].dbo.dim_patient dp ON dp.patient_id = pv.patient_id
            INNER JOIN [medical_database].dbo.dim_date do ON do.id = CONVERT(INT, FORMAT(pv.created_date, 'yyyyMMdd'))
            INNER JOIN [medical_database].dbo.dim_doctor dd ON dd.doctor_id = pv.doctor_id
            INNER JOIN [medical_database].dbo.dim_branch db ON db.branch_id = pv.branch_id
            INNER JOIN [medical_database].dbo.dim_treatment dt ON dt.treatment_id = pv.treatment_id
            INNER JOIN [medical_database].dbo.dim_visit_type dv ON dv.visit_type_id = pv.visit_type_id
            LEFT JOIN [medical_oltp].dbo.visit_diagnosis vd ON vd.visit_id = pv.id
            LEFT JOIN [medical_database].dbo.dim_diagnosis dg ON dg.diagnosis_id = vd.diagnosis_id
            LEFT JOIN [medical_oltp].dbo.doctor_feedback df ON df.visit_id = pv.id
            LEFT JOIN [medical_oltp].dbo.appointment a ON   a.id = pv.appointment_id 
            LEFT JOIN [medical_database].dbo.dim_appointment_type da ON a.appointment_type_id = da.appointment_type_id
            LEFT JOIN [medical_database].dbo.dim_date do1 ON do1.id = CONVERT(INT, FORMAT(pv.discharge_date, 'yyyyMMdd'))
            order by do.id;

        """
        oc.execute(query)
        rows = oc.fetchall()
        total_rows = len(rows)

        # ----------------------------
        # 3. LOAD: Updated INSERT for 9 columns
        # ----------------------------
        for r in rows:
            try:
                ac.execute("""
                    INSERT INTO fact_visit (
                        date_key, visit_type_key, doctor_key, patient_key,
                        appointment_type_key, branch_key, treatment_key,
                        diagnosis_key,discharge_key, rating
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,? )
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

        olap.commit()

        # ----------------------------
        # 4. Success Logging
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
        oltp.close()
        olap.close()