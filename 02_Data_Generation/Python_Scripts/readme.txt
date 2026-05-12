============================================================
HOSPITAL ERP / GENERIC DATA GENERATION PIPELINE
============================================================

This project generates LARGE, RELATIONAL, REALISTIC datasets
using Python + Faker.

It is DOMAIN-AGNOSTIC.
Hospital ERP is only ONE use case.
The SAME code can be reused for:
- K-12 School Systems
- Colleges / Universities
- Retail Chains
- Banking / Finance
- HR / Payroll
- Government Systems

------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------

Hospital Tables/
│
├── config.py
├── generators.py
├── data_generator.py
└── data/
    └── Hospital_ERP_Data.xlsx   (final output)

------------------------------------------------------------
FILE 1 — config.py
------------------------------------------------------------

PURPOSE:
--------
This file controls ONLY:
- HOW MUCH data is generated
- HOW BIG the system is
- PROBABILITIES & VOLUMES
- DATE RANGE

RULES:
------
❌ Never write Faker logic here
❌ Never write loops here
❌ Never create foreign keys here

✅ ONLY numbers, counts, probabilities, dates

MENTAL MODEL:
-------------
config.py answers ONE question:
👉 "HOW BIG IS THE WORLD?"

------------------------------------------------------------
WHAT TO CHANGE IN config.py
------------------------------------------------------------

If you want to change:
- Number of hospitals / schools
- Number of doctors / teachers
- Number of patients / students
- Visits per person
- Time range (years)
- Probabilities (feedback, billing, etc.)

👉 CHANGE config.py ONLY

------------------------------------------------------------
HOSPITAL → K-12 SCHOOL MAPPING (config.py)
------------------------------------------------------------

Hospital ERP            → K-12 School
-----------------------------------------
hospital_branches       → schools
departments             → classes / grades
doctors                 → teachers
patients                → students
treatments              → subjects
visits                  → attendance / exams
billing                 → fees

EXAMPLE:
--------
hospital_branches = 30   → schools = 10
doctors = 150             → teachers = 80
patients = 1000           → students = 2000

NO OTHER FILE NEEDS VOLUME CHANGES.

------------------------------------------------------------
FILE 2 — generators.py
------------------------------------------------------------

PURPOSE:
--------
Each function here generates EXACTLY ONE ROW
for EXACTLY ONE TABLE.

Example:
- gen_patient() → patient table
- gen_doctor() → doctor table
- gen_patient_visit() → visit table

Each function:
- Returns a dictionary
- Dictionary keys = column names
- Dictionary values = row values

MENTAL MODEL:
-------------
generators.py answers:
👉 "WHAT DOES ONE ROW LOOK LIKE?"

------------------------------------------------------------
WHAT TO CHANGE IN generators.py
------------------------------------------------------------

Change THIS file when you want to:
- Rename columns
- Add/remove columns
- Change business meaning of data
- Convert domain (Hospital → K-12)

DO NOT change:
- Row counts (config.py handles that)
- Execution order (data_generator.py handles that)

------------------------------------------------------------
HOSPITAL → K-12 FUNCTION MAPPING
------------------------------------------------------------

Hospital Function        → K-12 Function
-----------------------------------------
gen_patient              → gen_student
gen_doctor               → gen_teacher
gen_patient_visit        → gen_attendance / gen_exam
gen_treatment             → gen_subject
gen_billing              → gen_fees

You can rename functions OR keep names and change meaning.
Both are valid.

------------------------------------------------------------
EXAMPLE: Hospital Patient → K-12 Student
------------------------------------------------------------

def gen_patient(i, start_date, end_date):
    """
    Hospital: Patient
    K-12: Student
    """
    return {
        "id": i,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "dob": fake.date_of_birth(),   # still valid
        "gender": random.choice(["M","F"]),
        "created_date": created
    }

To convert:
- dob → enrollment_date (optional)
- patient → student (optional)

------------------------------------------------------------
FILE 3 — data_generator.py
------------------------------------------------------------

PURPOSE:
--------
This is the PIPELINE CONTROLLER.

It:
- Controls execution order
- Maintains foreign keys
- Registers IDs
- Writes the final Excel output

MENTAL MODEL:
-------------
data_generator.py answers:
👉 "HOW DOES EVERYTHING CONNECT?"

------------------------------------------------------------
DO NOT CHANGE LIGHTLY
------------------------------------------------------------

❌ IDRegistry logic
❌ Parent → child generation order
❌ Foreign key resolution logic

WHY?
-----
Because FK integrity depends on execution order.

------------------------------------------------------------
WHAT YOU CAN SAFELY CHANGE
------------------------------------------------------------

✅ Which generator is called
✅ Sheet names
✅ Domain logic (attendance vs visit)
✅ Business rules (OP/IP/DC → Exam/Attendance)

------------------------------------------------------------
HOSPITAL → K-12 LOGIC CHANGE EXAMPLE
------------------------------------------------------------

Hospital:
---------
OP / IP / DC

K-12:
-----
Attendance / Exam / Event

This logic belongs ONLY in data_generator.py

------------------------------------------------------------
ADDING A NEW TABLE (ANY DOMAIN)
------------------------------------------------------------

Example: student_marks (K-12)

STEP 1 — generators.py
---------------------
def gen_student_marks(i, student_id, subject_id):
    return {
        "id": i,
        "student_id": student_id,
        "subject_id": subject_id,
        "marks": random.randint(35, 100),
        "created_date": datetime.now()
    }

STEP 2 — data_generator.py
--------------------------
marks = []
for _ in range(1000):
    marks.append(
        gen_student_marks(
            marks_id,
            registry.get("student"),
            registry.get("subject")
        )
    )
    registry.register("student_marks", marks_id)
    marks_id += 1

STEP 3 — OUTPUT
---------------
write_excel("student_marks", marks, workbook)

NO OTHER FILE NEEDS CHANGES.

------------------------------------------------------------
FINAL GOLDEN RULES (MEMORIZE THIS)
------------------------------------------------------------

📦 config.py
→ "How big is the world?"

🧬 generators.py
→ "What does ONE row look like?"

🧠 data_generator.py
→ "How do all tables connect?"

------------------------------------------------------------
ONE-LINE TEAM EXPLANATION
------------------------------------------------------------

"Change numbers in config, change meaning in generators,
and never break the pipeline in data_generator."

============================================================
NEXT OF DOCUMENT
============================================================

"""
====================================================
CONFIGURATION FILE (config.py)
====================================================

👉 PURPOSE:
This file controls:
- HOW MUCH data is generated
- FOR HOW LONG (date range)
- PROBABILITIES & VOLUMES
- DOMAIN-SPECIFIC SIZES

⚠️ RULE:
❌ Never hardcode numbers inside generator functions
✅ Always change numbers ONLY here

----------------------------------------------------
HOW TO CONVERT TO K-12 SCHOOL SYSTEM
----------------------------------------------------

Hospital ERP        → K-12 School
-----------------------------------------
hospital_branches  → schools
departments        → grades / classes
doctors            → teachers
patients           → students
visits             → attendance / exams
billing            → fees

👉 To convert domain:
1. Rename config keys (optional but recommended)
2. Adjust volumes (schools < hospitals, teachers < doctors)
3. Generator logic will use these values automatically
"""

from datetime import date

CONFIG = {
    # ========================
    # OUTPUT
    # ========================
    "output_folder": "data",

    # ========================
    # GEOGRAPHY
    # ========================
    "states": 5,
    "cities": 20,

    # ========================
    # HOSPITAL / SCHOOL STRUCTURE
    # ========================
    "hospital_branches": 30,      # K-12: number of schools
    "departments_per_branch": 5,  # K-12: classes per school
    "specializations": 20,        # K-12: subjects
    "doctors": 150,               # K-12: teachers

    # ========================
    # ROOMS / CLASSROOMS
    # ========================
    "room_types": 6,
    "rooms_per_branch": 20,

    # ========================
    # STUDENTS / PATIENTS
    # ========================
    "patients": 1000,             # K-12: students

    # Each patient/student can have multiple visits
    "visits_per_patient_min": 1,
    "visits_per_patient_max": 5,

    # ========================
    # TRANSACTIONAL DATA
    # ========================
    "treatments": 15,              # K-12: subjects / exams
    "pharmacy_items": 30,           # K-12: books / supplies
    "radiology_services": 15,       # K-12: labs / activities

    # ========================
    # PROBABILITIES
    # ========================
    "feedback_probability": 0.30,

    "pharmacy_billing_detail_probability": 0.7,
    "radiology_billing_detail_probability": 0.6,

    "pharmacy_items_per_bill_min": 1,
    "pharmacy_items_per_bill_max": 5,

    "radiology_items_per_bill_min": 1,
    "radiology_items_per_bill_max": 2,

    # ========================
    # TIME CONTROL
    # ========================
    "start_date": date(2024, 1, 1),
    "duration_years": 2,

    # ========================
    # MEMORY SAFETY
    # ========================
    "max_active_ids": 200_000,
}
----------------------------
PART 2#
---------------------------
"""
====================================================
GENERATORS FILE (generators.py)
====================================================

👉 PURPOSE:
Each function here generates ONE ROW for ONE TABLE.

Example:
- gen_patient() → patient table
- gen_doctor() → doctor table
- gen_patient_visit() → visit table

----------------------------------------------------
HOW TO CONVERT TO K-12 SCHOOL
----------------------------------------------------

Hospital ERP         → K-12 School
-----------------------------------------
gen_patient          → gen_student
gen_doctor           → gen_teacher
gen_patient_visit    → gen_attendance / gen_exam
gen_treatment        → gen_subject
gen_billing          → gen_fees

⚠️ IMPORTANT:
- Function signatures stay SAME STYLE
- Only internal field names & meanings change
"""

# =========================
# EXAMPLE: PATIENT → STUDENT
# =========================

def gen_patient(i, start_date, end_date):
    """
    HOSPITAL:
        patient record
    K-12:
        student record

    👉 To convert:
    - rename function to gen_student (optional)
    - change dob → enrollment_date
    - change gender → gender (same)
    """
    created = random_datetime_between(start_date, end_date)

    return {
        "id": i,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "dob": fake.date_of_birth(),  # K-12: date_of_birth OK
        "gender": random.choice(["M", "F"]),
        "created_date": created,
        "created_by": "system",
    }

-----------------------------------
PART 3#
-----------------------------------
"""
====================================================
MAIN PIPELINE (data_generator.py)
====================================================

👉 PURPOSE:
- Controls execution order
- Maintains foreign keys
- Writes final Excel output

----------------------------------------------------
DO NOT CHANGE LIGHTLY
----------------------------------------------------
- IDRegistry logic
- Write order
- Parent → Child table sequence

----------------------------------------------------
HOW TO CONVERT TO K-12 SCHOOL
----------------------------------------------------

STEP 1: Rename table labels (optional)
    "patient" → "student"
    "doctor" → "teacher"

STEP 2: Replace generator calls
    gen_patient → gen_student
    gen_doctor → gen_teacher

STEP 3: Adjust visit logic
    OP/IP/DC → Attendance / Exam / Event
"""

# =========================
# ID REGISTRY
# =========================
class IDRegistry:
    """
    Stores generated IDs for FK resolution

    Example:
    - patient.id stored
    - patient_visit.patient_id pulls from registry

    ⚠️ NEVER BYPASS THIS
    """

-----------------------------------
PART 4#
-----------------------------------
"""
ADDING A NEW TABLE (EXAMPLE)
----------------------------

Example: K-12 → student_marks table

1️⃣ Add generator in generators.py
---------------------------------
def gen_student_marks(i, student_id, subject_id):
    return {
        "id": i,
        "student_id": student_id,
        "subject_id": subject_id,
        "marks": random.randint(35, 100)
    }

2️⃣ Register IDs in data_generator.py
------------------------------------
registry.register("student_marks", marks_id)

3️⃣ Write CSV / Excel sheet
--------------------------
write_excel("student_marks", rows, workbook)
"""

============================================================
HOSPITAL ERP / GENERIC DATA GENERATION PIPELINE
============================================================

This project generates LARGE, RELATIONAL, REALISTIC datasets
using Python + Faker.

The system is DOMAIN-AGNOSTIC.
Hospital ERP is just ONE use case.

The SAME pipeline can be reused for:
- K-12 School Systems
- Colleges / Universities
- Retail Chains
- Banking / Finance
- HR / Payroll
- Government Systems

============================================================
PROJECT STRUCTURE
============================================================

Hospital Tables/
│
├── config.py           → Controls SIZE & VOLUME
├── generators.py       → Defines ONE ROW per table
├── data_generator.py   → Pipeline & FK orchestration
└── data/
    └── Hospital_ERP_Data.xlsx   → Final output (one sheet per table)

============================================================
FILE 1 — config.py
============================================================

PURPOSE
-------
Controls ONLY:
- How much data is generated
- How big the system is
- Probabilities & distributions
- Time range

RULES
-----
❌ No Faker logic
❌ No loops
❌ No foreign keys
❌ No business logic

✅ ONLY numbers, counts, probabilities, dates

MENTAL MODEL
------------
config.py answers ONE question:
👉 “HOW BIG IS THE WORLD?”

------------------------------------------------------------
WHAT TO CHANGE IN config.py
------------------------------------------------------------

Change THIS file if you want to adjust:
- Number of hospitals / schools
- Number of doctors / teachers
- Number of patients / students
- Visits per person
- Date range
- Feedback / billing probabilities

👉 NEVER change generators.py for volume control

------------------------------------------------------------
HOSPITAL → K-12 SCHOOL MAPPING (config.py)
------------------------------------------------------------

Hospital ERP            → K-12 School
-----------------------------------------
hospital_branches       → schools
departments             → grades / classes
doctors                 → teachers
patients                → students
treatments              → subjects
visits                  → attendance / exams
billing                 → fees

Example:
--------
hospital_branches = 30   → schools = 10
doctors = 150             → teachers = 80
patients = 1000           → students = 2000

No other file needs volume changes.

============================================================
FILE 2 — generators.py
============================================================

PURPOSE
-------
Each function generates EXACTLY ONE ROW
for EXACTLY ONE TABLE.

Example:
- gen_patient() → patient table
- gen_doctor() → doctor table
- gen_patient_visit() → visit table

Each function:
- Returns a dictionary
- Keys = column names
- Values = column values

MENTAL MODEL
------------
generators.py answers:
👉 “WHAT DOES ONE ROW LOOK LIKE?”

------------------------------------------------------------
WHAT TO CHANGE IN generators.py
------------------------------------------------------------

Change THIS file if you want to:
- Rename columns
- Add / remove columns
- Change business meaning of data
- Convert domain (Hospital → K-12)

DO NOT change:
- Row counts (config.py controls this)
- Execution order (data_generator.py controls this)

------------------------------------------------------------
HOSPITAL → K-12 FUNCTION MAPPING
------------------------------------------------------------

Hospital Function        → K-12 Function
-----------------------------------------
gen_patient              → gen_student
gen_doctor               → gen_teacher
gen_patient_visit        → gen_attendance / gen_exam
gen_treatment             → gen_subject
gen_billing              → gen_fees

You may rename functions OR keep names and change meaning.
Both approaches are valid.

------------------------------------------------------------
EXAMPLE: Patient → Student
------------------------------------------------------------

def gen_patient(i, start_date, end_date):
    """
    Hospital: Patient
    K-12: Student
    """
    return {
        "id": i,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "dob": fake.date_of_birth(),   # OK for K-12
        "gender": random.choice(["M","F"]),
        "created_date": created
    }

Optional changes:
- dob → enrollment_date
- patient → student

============================================================
FILE 3 — data_generator.py
============================================================

PURPOSE
-------
This is the PIPELINE CONTROLLER.

It:
- Controls execution order
- Maintains foreign keys
- Registers IDs
- Writes the final Excel file

MENTAL MODEL
------------
data_generator.py answers:
👉 “HOW DOES EVERYTHING CONNECT?”

------------------------------------------------------------
DO NOT CHANGE LIGHTLY
------------------------------------------------------------

❌ IDRegistry logic
❌ Parent → child generation order
❌ Foreign key resolution logic

WHY?
-----
Foreign-key integrity depends on execution order.

------------------------------------------------------------
WHAT YOU CAN SAFELY CHANGE
------------------------------------------------------------

✅ Which generator functions are called
✅ Sheet / table names
✅ Domain logic (attendance vs visit)
✅ Business rules (OP/IP/DC → Exam/Attendance)

------------------------------------------------------------
HOSPITAL → K-12 LOGIC CHANGE EXAMPLE
------------------------------------------------------------

Hospital:
---------
OP / IP / DC

K-12:
-----
Attendance / Exam / Event

This logic belongs ONLY in data_generator.py

============================================================
ADDING A NEW TABLE (ANY DOMAIN)
============================================================

Example: student_marks (K-12)

STEP 1 — generators.py
---------------------
def gen_student_marks(i, student_id, subject_id):
    return {
        "id": i,
        "student_id": student_id,
        "subject_id": subject_id,
        "marks": random.randint(35, 100),
        "created_date": datetime.now()
    }

STEP 2 — data_generator.py
--------------------------
marks = []
for _ in range(1000):
    marks.append(
        gen_student_marks(
            marks_id,
            registry.get("student"),
            registry.get("subject")
        )
    )
    registry.register("student_marks", marks_id)
    marks_id += 1

STEP 3 — OUTPUT
---------------
write_excel("student_marks", rows, workbook)

NO OTHER FILE NEEDS CHANGES.

============================================================
FINAL GOLDEN RULES
============================================================

📦 config.py
→ “How big is the world?”

🧬 generators.py
→ “What does ONE row look like?”

🧠 data_generator.py
→ “How do all tables connect?”

------------------------------------------------------------
ONE-LINE TEAM EXPLANATION
------------------------------------------------------------

“Change numbers in config, change meaning in generators,
and never break the pipeline in data_generator.”

============================================================
END OF DOCUMENT
============================================================