

import pyodbc

def get_oltp_conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=10.10.10.73;"
        "DATABASE=medical_oltp;"
        "UID=sa;"
        "PWD=Tech#ish$it25;"
        "TrustServerCertificate=yes;"
    )

def get_olap_conn():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=10.10.10.73;"
        "DATABASE=medical_database;"
        "UID=sa;"
        "PWD=Tech#ish$it25;"
        "TrustServerCertificate=yes;"
    )