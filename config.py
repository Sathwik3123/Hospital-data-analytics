from datetime import date

CONFIG = {
    # ======================
    # OUTPUT
    # ======================
    "output_folder": "data",

    # ======================
    # GEOGRAPHY / STRUCTURE
    # ======================
    "states": 5,
    "cities": 20,
    "hospital_branches": 30,

    "departments_per_branch": 5,
    "specializations": 20,
    "doctors": 150,

    # ======================
    # ROOMS
    # ======================
    "room_types": 6,
    "rooms_per_branch": 20,

    # ======================
    # MEDICAL MASTER DATA
    # ======================
    "treatments": 15,
    "pharmacy_items": 30,
    "radiology_services": 15,

    # ======================
    # HIGH VOLUME DATA
    # ======================
    "patients": 1000,
    "visits_per_patient_min": 1,
    "visits_per_patient_max": 5,
    
    # ======================
    # BILLING DETAILS
    # ======================
    "pharmacy_billing_detail_probability": 0.5,  # 50% of pharmacy bills have details
    "radiology_billing_detail_probability": 0.8,  # 80% of radiology bills have details
    "pharmacy_items_per_bill_min": 1,
    "pharmacy_items_per_bill_max": 5,
    "radiology_items_per_bill_min": 1,
    "radiology_items_per_bill_max": 3,
    
    # ======================
    # FEEDBACK
    # ======================
    "feedback_probability": 0.3,  # 30% of patients leave feedback

    # ======================
    # TIME CONTROL
    # ======================
    "start_date": date(2024, 1, 1),
    "duration_years": 2,   # 2 or 2.5 supported

    # ======================
    # MEMORY SAFETY
    # ======================
    "max_active_ids": 500_000
}