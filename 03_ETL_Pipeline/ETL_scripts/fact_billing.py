import os
import audit  # Updated audit.py for new logging
from connection import get_oltp_conn, get_olap_conn

def load_fact_billing():
    """
    ETL process to load detailed billing data from OLTP into OLAP 'fact_billing'.
    Updated to include granular keys and pre-calculated totals.
    """

    file_name = os.path.basename(__file__)
    table_name = "fact_billing"

    total_rows = 0
    rows_processed = 0
    rows_failed = 0

    oltp = get_oltp_conn()
    olap = get_olap_conn()
    oc = oltp.cursor()
    ac = olap.cursor()

    try:
        # ----------------------------
        # 2. EXTRACT: New granular query
        # ----------------------------
        query = """
            
     SELECT 
                do.id as date_key,
                dd.id AS doctor_key,
                dpy.id AS payment_type_key,
                dvt.id as visit_type_key,
                db.id AS branch_key,
                dp.id AS patient_key,
                dt.id AS treatment_key,
                dg.id as diagnosis_key,
                b.treatment_charge,              
                b.appointment_charge,
                b.room_charge,
                ISNULL(rad.radsum, 0) as radsum,
                ISNULL(pharma.pharmsum, 0) as pharmsum,
                (ISNULL(b.treatment_charge, 0) + 
                 ISNULL(b.appointment_charge, 0) + 
                 ISNULL(b.room_charge, 0) + 
                 ISNULL(rad.radsum, 0) + 
                 ISNULL(pharma.pharmsum, 0)) as total_amount
            FROM [medical_oltp].dbo.patient_visit pv
            JOIN [medical_oltp].dbo.billing b ON pv.id=b.patient_visit_id
            JOIN [medical_database].dbo.dim_date do ON do.id = CONVERT(INT, FORMAT(b.created_date, 'yyyyMMdd'))
            LEFT JOIN (
                SELECT patient_visit_id, SUM(total_amount) as radsum 
                FROM [medical_oltp].dbo.radiology_billing_detail 
                GROUP BY patient_visit_id
            ) rad ON pv.id = rad.patient_visit_id
            LEFT JOIN (
                SELECT patient_visit_id, SUM(total_price) as pharmsum 
                FROM [medical_oltp].dbo.pharmacy_billing_detail 
                GROUP BY patient_visit_id
            ) pharma ON pv.id = pharma.patient_visit_id
            JOIN [medical_database].dbo.dim_patient dp ON dp.patient_id = pv.patient_id
            JOIN [medical_database].dbo.dim_doctor dd ON dd.doctor_id = pv.doctor_id
            JOIN [medical_database].dbo.dim_branch db ON db.branch_id = b.hospital_branch_id
            JOIN [medical_database].dbo.dim_treatment dt ON dt.treatment_id = pv.treatment_id
            JOIN [medical_database].dbo.dim_payment_type dpy ON dpy.payment_type_id = b.payment_type_id
            join [medical_database].dbo.dim_visit_type dvt on dvt.visit_type_id=pv.visit_type_id
             LEFT JOIN [medical_oltp].dbo.visit_diagnosis vd ON vd.visit_id = pv.id
             LEFT JOIN [medical_database].dbo.dim_diagnosis dg ON dg.diagnosis_id = vd.diagnosis_id
            order by do.id;

        """
        oc.execute(query)
        rows = oc.fetchall()
        total_rows = len(rows)

        # ----------------------------
        # 3. LOAD: Updated INSERT for new columns
        # ----------------------------
        for r in rows:
            try:
                ac.execute("""
                    INSERT INTO fact_billing (
                        date_key, doctor_key, payment_type_key,visit_type_key, branch_key, 
                        patient_key, treatment_key,diagnosis_key, treatment_charges, 
                        appointment_charges, room_charges, radiology_charges, 
                        pharmacy_charges, total_amount
                    ) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,? )
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
        oltp.close()
        olap.close()