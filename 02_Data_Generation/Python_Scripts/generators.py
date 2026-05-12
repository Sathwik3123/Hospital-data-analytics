from faker import Faker
from datetime import datetime, timedelta, date
import random

fake = Faker()

SYSTEM_USER = "system"

# =========================
# DATE RANGE HELPER
# =========================
def get_date_range(start_date, duration_years):
    """Calculate date range for data generation"""
    total_days = int(duration_years * 365)
    end_date = start_date + timedelta(days=total_days)
    return start_date, end_date


def random_datetime_between(start_date, end_date):
    """Generate random datetime between two dates (safe)"""

    if isinstance(start_date, date) and not isinstance(start_date, datetime):
        start_date = datetime.combine(start_date, datetime.min.time())
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.min.time())

    # ✅ SAFETY CHECK (THE FIX)
    if start_date >= end_date:
        return start_date

    time_between = end_date - start_date
    days_between = time_between.days

    random_days = random.randint(0, days_between)
    random_seconds = random.randint(0, 86399)

    return start_date + timedelta(days=random_days, seconds=random_seconds)


# =========================
# STATE / CITY
# =========================
def gen_state(i):
    """Generate state record"""
    now = datetime.now()
    return {
        "id": i,
        "name": fake.state(),
        "description": "",
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


def gen_city(i, state_id):
    """Generate city record"""
    now = datetime.now()
    return {
        "id": i,
        "name": fake.city(),
        "state_id": state_id,
        "longitude": round(random.uniform(-180, 180), 6),
        "latitude": round(random.uniform(-90, 90), 6),
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# HOSPITAL BRANCH
# =========================
def gen_hospital_branch(i, city_id):
    """Generate hospital branch record"""
    now = datetime.now()
    return {
        "id": i,
        "name": f"{fake.company()} Hospital",
        "city_id": city_id,
        "address": fake.address(),
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# SPECIALIZATION / DEPARTMENT
# =========================
SPECIALIZATIONS = [
    "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology",
    "Dermatology", "Psychiatry", "Radiology", "Anesthesiology", "Pathology",
    "General Surgery", "Emergency Medicine", "Internal Medicine", "Obstetrics",
    "Ophthalmology", "ENT", "Urology", "Nephrology", "Gastroenterology", "Endocrinology"
]

DEPARTMENTS = [
    "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology",
    "Emergency", "Surgery", "ICU", "Laboratory", "Radiology",
    "Pharmacy", "Administration", "OPD", "IPD", "Physiotherapy"
]


def gen_specialization(i):
    """Generate specialization record"""
    now = datetime.now()
    # Use predetermined specializations to avoid duplicates
    spec_name = SPECIALIZATIONS[(i - 1) % len(SPECIALIZATIONS)]
    return {
        "id": i,
        "name": spec_name,
        "description": f"{spec_name} specialization",
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


def gen_department(i, hospital_branch_id):
    """Generate department record"""
    now = datetime.now()
    # Use predetermined departments to avoid duplicates
    dept_name = DEPARTMENTS[(i - 1) % len(DEPARTMENTS)]
    return {
        "id": i,
        "name": dept_name,
        "description": f"{dept_name} department",
        "hospital_branch_id": hospital_branch_id,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# DOCTOR
# =========================
def gen_doctor(i, department_id, specialization_id):
    """Generate doctor record"""
    now = datetime.now()
    return {
        "id": i,
        "first_name": fake.first_name(),
        "middle_name": fake.first_name() if random.random() > 0.7 else "",
        "last_name": fake.last_name(),
        "specialization_id": specialization_id,
        "department_id": department_id,
        "phone": fake.phone_number()[:20],
        "email": fake.email(),
        "reg_number": fake.bothify("REG-#####"),
        "is_active": True,
        "is_hod": False,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# ROOM TYPE / ROOM
# =========================
ROOM_TYPES = ["ICU", "General", "Private", "Semi-Private", "Emergency", "OT"]


def gen_room_type(i):
    """Generate room type record"""
    now = datetime.now()
    # Use predetermined room types to avoid duplicates
    room_type_name = ROOM_TYPES[(i - 1) % len(ROOM_TYPES)]
    return {
        "id": i,
        "name": room_type_name,
        "description": f"{room_type_name} room type",
        "is_active": True,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


def gen_room(i, room_type_id, hospital_branch_id):
    """Generate room record"""
    now = datetime.now()
    # 90% rooms are available, 10% not available
    status = "A" if random.random() > 0.1 else "NA"
    
    # Different charges based on room type
    base_charges = {1: 5000, 2: 2000, 3: 10000, 4: 7000, 5: 3000, 6: 15000}
    base_charge = base_charges.get(room_type_id, 5000)
    charge = round(base_charge + random.uniform(-1000, 3000), 2)
    
    return {
        "id": i,
        "hospital_branch_id": hospital_branch_id,
        "room_type_id": room_type_id,
        "status": status,
        "charge_per_day": charge,
        "is_active": True,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# PATIENT
# =========================
def gen_patient(i, start_date, end_date):
    """Generate patient record"""
    # Patient created date is random within the date range
    created = random_datetime_between(start_date, end_date)
    
    # Some patients have updates (30% chance)
    updated = None
    if random.random() < 0.3:
        updated = random_datetime_between(created, end_date)
    
    return {
        "id": i,
        "first_name": fake.first_name(),
        "middle_name": fake.first_name() if random.random() > 0.7 else "",
        "last_name": fake.last_name(),
        "dob": fake.date_of_birth(minimum_age=1, maximum_age=90),
        "gender": random.choice(["M", "F"]),
        "phone": fake.phone_number()[:20],
        "email": fake.email(),
        "address": fake.address()[:255],
        "created_date": created,
        "created_by": SYSTEM_USER,
        "updated_date": updated,
        "updated_by": SYSTEM_USER if updated else None,
    }


# =========================
# VISIT TYPE (STATIC)
# =========================
def gen_visit_types():
    """Generate visit type records (static)"""
    now = datetime.now()
    return [
        {
            "id": 1,
            "code": "OP",
            "name": "Out Patient",
            "description": "Outpatient consultation",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 2,
            "code": "IP",
            "name": "In Patient",
            "description": "Inpatient admission",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 3,
            "code": "DC",
            "name": "Day Care",
            "description": "Day care treatment",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
    ]


# =========================
# TREATMENT
# =========================
TREATMENTS = [
    ("Physiotherapy", "Therapy"),
    ("Appendectomy", "Surgery"),
    ("Dialysis", "Therapy"),
    ("Chemotherapy", "Therapy"),
    ("MRI Scan", "Consultation"),
    ("CT Scan", "Consultation"),
    ("Blood Test", "Consultation"),
    ("X-Ray", "Consultation"),
    ("ECG", "Consultation"),
    ("Endoscopy", "Surgery"),
    ("Colonoscopy", "Surgery"),
    ("Ultrasound", "Consultation"),
    ("Biopsy", "Surgery"),
    ("Cataract Surgery", "Surgery"),
    ("Knee Replacement", "Surgery"),
]


def gen_treatment(i):
    """Generate treatment record"""
    now = datetime.now()
    treatment_name, category = TREATMENTS[(i - 1) % len(TREATMENTS)]
    return {
        "id": i,
        "name": treatment_name,
        "category": category,
        "description": f"{treatment_name} - {category}",
        "is_active": True,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# APPOINTMENT
# =========================
def gen_appointment(i, patient_id, doctor_id, hospital_branch_id, patient_created_date, start_date, end_date):
    """Generate appointment record"""
    # Appointment created after patient record was created
    created = random_datetime_between(patient_created_date, end_date)
    
    # Appointment date is after created date
    appointment_date = random_datetime_between(created, end_date)
    
    # Appointment status
    status = random.choices(
        ["Booked", "Completed", "Cancelled"],
        weights=[0.2, 0.7, 0.1],  # 70% completed, 20% booked, 10% cancelled
        k=1
    )[0]
    
    return {
        "id": i,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "hospital_branch_id": hospital_branch_id,
        "appointment_date": appointment_date,
        "appointment_status": status,
        "created_date": created,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# BILLING TYPE (STATIC)
# =========================
def gen_billing_types():
    """Generate billing type records (static)"""
    now = datetime.now()
    return [
        {
            "id": 1,
            "name": "Pharmacy",
            "description": "Pharmacy and medication charges",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 2,
            "name": "Radiology",
            "description": "Radiology and imaging charges",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 3,
            "name": "Consultation",
            "description": "Doctor consultation charges",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 4,
            "name": "Surgery",
            "description": "Surgery and operation charges",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 5,
            "name": "Misc",
            "description": "Miscellaneous charges",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
    ]


# =========================
# PATIENT VISIT
# =========================
def gen_patient_visit(
    i,
    patient_id,
    doctor_id,
    hospital_branch_id,
    visit_type_id,
    appointment_id,
    treatment_id,
    room_id,
    patient_created_date,
    start_date,
    end_date,
):
    """Generate patient visit record with proper chronology"""
    
    # Visit created after patient was created
    created = random_datetime_between(patient_created_date, end_date)
    
    # Admission date is on or after created date
    admit_date = fake.date_between(
        start_date=created.date() if isinstance(created, datetime) else created,
        end_date=end_date
    )
    
    # Discharge date logic depends on visit type
    if visit_type_id == 1:  # OP - same day discharge
        discharge_date = admit_date
    elif visit_type_id == 3:  # DC - same day or next day
        max_days = 1
        discharge_date = fake.date_between(
            start_date=admit_date,
            end_date=min(admit_date + timedelta(days=max_days), end_date)
        )
    else:  # IP - 1 to 10 days
        max_days = random.randint(1, 10)
        discharge_date = fake.date_between(
            start_date=admit_date,
            end_date=min(admit_date + timedelta(days=max_days), end_date)
        )
    
    return {
        "id": i,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "treatment_id": treatment_id,
        "appointment_id": appointment_id,
        "hospital_branch_id": hospital_branch_id,
        "visit_type_id": visit_type_id,
        "admission_date": admit_date,
        "discharge_date": discharge_date,
        "prescription": None,  # BLOB - would need binary data
        "room_id": room_id,
        "created_date": created,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# BILLING
# =========================
def gen_billing(i, patient_visit_id, hospital_branch_id, billing_type_id):
    """Generate billing record"""
    now = datetime.now()
    
    # Amount varies by billing type
    amount_ranges = {
        1: (500, 5000),      # Pharmacy
        2: (1000, 15000),    # Radiology
        3: (500, 3000),      # Consultation
        4: (10000, 100000),  # Surgery
        5: (200, 2000),      # Misc
    }
    min_amt, max_amt = amount_ranges.get(billing_type_id, (1000, 10000))
    total_amount = round(random.uniform(min_amt, max_amt), 2)
    
    # Payment status: 80% success, 15% failed, 5% rejected
    payment_status = random.choices(
        ["S", "F", "R"],
        weights=[0.80, 0.15, 0.05],
        k=1
    )[0]
    
    return {
        "id": i,
        "patient_visit_id": patient_visit_id,
        "billing_type_id": billing_type_id,
        "hospital_branch_id": hospital_branch_id,
        "total_amount": total_amount,
        "payment_status": payment_status,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# PHARMACY ITEMS
# =========================
PHARMACY_ITEMS = [
    ("Paracetamol 500mg", "Pain relief medication", 50.00),
    ("Amoxicillin 250mg", "Antibiotic", 120.00),
    ("Ibuprofen 400mg", "Anti-inflammatory", 80.00),
    ("Omeprazole 20mg", "Antacid", 150.00),
    ("Metformin 500mg", "Diabetes medication", 100.00),
    ("Aspirin 75mg", "Blood thinner", 60.00),
    ("Cetirizine 10mg", "Antihistamine", 40.00),
    ("Azithromycin 500mg", "Antibiotic", 200.00),
    ("Losartan 50mg", "Blood pressure medication", 180.00),
    ("Atorvastatin 10mg", "Cholesterol medication", 250.00),
    ("Insulin Glargine", "Diabetes injection", 500.00),
    ("Salbutamol Inhaler", "Asthma inhaler", 350.00),
    ("Vitamin D3 60K", "Vitamin supplement", 90.00),
    ("Calcium Tablets", "Mineral supplement", 70.00),
    ("Cough Syrup", "Cough suppressant", 85.00),
]


def gen_pharmacy_item(i):
    """Generate pharmacy item record"""
    now = datetime.now()
    name, description, base_price = PHARMACY_ITEMS[(i - 1) % len(PHARMACY_ITEMS)]
    # Add slight price variation
    price = round(base_price + random.uniform(-10, 20), 2)
    
    return {
        "id": i,
        "name": name,
        "description": description,
        "price": price,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# PHARMACY BILLING DETAIL
# =========================
def gen_pharmacy_billing_detail(i, billing_id, item_id):
    """Generate pharmacy billing detail record"""
    now = datetime.now()
    
    quantity = random.randint(1, 10)
    duration_options = ["7D", "14D", "21D", "1M", "2M", "3M"]
    prescribed_duration = random.choice(duration_options)
    
    return {
        "id": i,
        "billing_id": billing_id,
        "item_id": item_id,
        "quantity": quantity,
        "prescribed_duration": prescribed_duration,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# RADIOLOGY SERVICE
# =========================
RADIOLOGY_SERVICES = [
    ("X-Ray Chest", "Chest X-Ray imaging", 500.00),
    ("CT Scan Head", "CT scan of head", 3500.00),
    ("MRI Brain", "MRI scan of brain", 6000.00),
    ("Ultrasound Abdomen", "Abdominal ultrasound", 1200.00),
    ("ECG", "Electrocardiogram", 300.00),
    ("Echo Cardiogram", "Heart ultrasound", 2000.00),
    ("Mammography", "Breast imaging", 1500.00),
    ("Bone Density Scan", "DEXA scan", 1800.00),
    ("X-Ray Spine", "Spine X-Ray", 600.00),
    ("CT Scan Abdomen", "CT scan of abdomen", 4000.00),
    ("MRI Spine", "MRI of spine", 7000.00),
    ("Ultrasound Pelvis", "Pelvic ultrasound", 1000.00),
    ("Doppler Study", "Blood flow study", 2500.00),
    ("PET Scan", "Positron emission tomography", 15000.00),
    ("Angiography", "Blood vessel imaging", 8000.00),
]


def gen_radiology_service(i):
    """Generate radiology service record"""
    now = datetime.now()
    name, description, base_price = RADIOLOGY_SERVICES[(i - 1) % len(RADIOLOGY_SERVICES)]
    # Add slight price variation
    price = round(base_price + random.uniform(-100, 200), 2)
    
    return {
        "id": i,
        "name": name,
        "description": description,
        "price": price,
        "is_active": True,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# RADIOLOGY BILLING DETAIL
# =========================
def gen_radiology_billing_detail(i, billing_id, item_id):
    """Generate radiology billing detail record"""
    now = datetime.now()
    
    # Usually quantity is 1 for radiology services
    quantity = random.choices([1, 2], weights=[0.9, 0.1], k=1)[0]
    
    # Prescribed duration not really applicable but keeping for consistency
    prescribed_duration = ""
    
    return {
        "id": i,
        "billing_id": billing_id,
        "item_id": item_id,
        "quantity": quantity,
        "prescribed_duration": prescribed_duration,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }


# =========================
# FEEDBACK TYPE (STATIC)
# =========================
def gen_feedback_types():
    """Generate feedback type records (static)"""
    now = datetime.now()
    return [
        {
            "id": 1,
            "name": "Service Quality",
            "description": "Feedback about service quality",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 2,
            "name": "Doctor Consultation",
            "description": "Feedback about doctor consultation",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 3,
            "name": "Cleanliness",
            "description": "Feedback about hospital cleanliness",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 4,
            "name": "Staff Behavior",
            "description": "Feedback about staff behavior",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
        {
            "id": 5,
            "name": "Facilities",
            "description": "Feedback about hospital facilities",
            "is_active": True,
            "created_date": now,
            "created_by": SYSTEM_USER,
            "updated_date": None,
            "updated_by": None,
        },
    ]


# =========================
# FEEDBACK
# =========================
FEEDBACK_COMMENTS = [
    "Excellent service and care",
    "Very satisfied with the treatment",
    "Doctor was very professional",
    "Long waiting time",
    "Staff was helpful and courteous",
    "Clean and well-maintained facility",
    "Could improve communication",
    "Great experience overall",
    "Need better parking facilities",
    "Highly recommend this hospital",
]


def gen_feedback(i, patient_id, feedback_type_id):
    """Generate feedback record"""
    now = datetime.now()
    
    description = random.choice(FEEDBACK_COMMENTS)
    
    return {
        "id": i,
        "patient_id": patient_id,
        "description": description,
        "feedback_type_id": feedback_type_id,
        "created_date": now,
        "created_by": SYSTEM_USER,
        "updated_date": None,
        "updated_by": None,
    }