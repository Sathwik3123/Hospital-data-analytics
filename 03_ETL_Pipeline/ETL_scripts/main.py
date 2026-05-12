import dim_date
import dim_patient
import dim_doctor
import dim_branch
import dim_treatment
import dim_visit_type
import dim_appointment_type
import dim_payment_type
import dim_diagnosis
import fact_visit
import fact_billing
import audit

def safe_run(loader_function, file_name):
    """
    Executes a loader function safely.
    Logs any exceptions via audit.log_etl_event without stopping the ETL pipeline.
    """
    try:
        loader_function()
    except Exception as e:
        # Log failure for this specific loader
        audit.log_etl_event(
            file_name=file_name,
            status="PROCESS_FAILED",
            total_rows=0,
            rows_processed=0,
            rows_failed=0,
            
        )


def run_etl():
    """
    Run all ETL loader functions sequentially.
    Each loader is wrapped in safe_run to avoid breaking the pipeline on errors.
    """

    # ----------------------------
    # 1️⃣ Static Dimensions
    # ----------------------------
    safe_run(dim_date.load_date, "dim_date.py")
    safe_run(dim_visit_type.load_visit_type, "dim_visit_type.py")
    safe_run(dim_appointment_type.load_appointment_type, "dim_appointment_type.py")
    safe_run(dim_payment_type.load_payment_type, "dim_payment_type.py")

    # ----------------------------
    # 2️⃣ Master Dimensions
    # ----------------------------
    safe_run(dim_branch.load_branch, "dim_branch.py")
    safe_run(dim_treatment.load_treatment, "dim_treatment.py")
    safe_run(dim_doctor.load_doctor, "dim_doctor.py")
    safe_run(dim_patient.load_patient, "dim_patient.py")
    safe_run(dim_diagnosis.load_diagnosis,"dim_diagnosis.py")

    # ----------------------------
    # 3️⃣ Fact Tables
    # ----------------------------
    safe_run(fact_visit.load_fact_visit, "fact_visit.py")
    safe_run(fact_billing.load_fact_billing, "fact_billing.py")


if __name__ == "__main__":
    run_etl()

    