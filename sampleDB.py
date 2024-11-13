import sqlite3
from faker import Faker

fake = Faker()

# Function to generate realistic data
def generate_realistic_data():
    first_name = fake.first_name()
    last_name = fake.last_name()
    gender = fake.random_element(["Male", "Female"])
    ethnicity = fake.random_element(["White", "Black or African American", "Asian", "Hispanic or Latino", "Native American", "Other"])
    address = fake.street_address()
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()
    phone = fake.phone_number()
    email = fake.email()
    language_preference = fake.random_element(["English", "Spanish", "Chinese", "French", "Arabic"])
    socioeconomic_status = fake.random_element(["Low income", "Middle income", "High income"])
    special_need = fake.random_element(["Wheelchair accessibility", "Vision impairment", "Hearing impairment"])

    return (
        first_name,
        last_name,
        gender,
        ethnicity,
        address,
        city,
        state,
        zip_code,
        phone,
        email,
        language_preference,
        socioeconomic_status,
        special_need
    )

# Connect to SQLite database
conn = sqlite3.connect('health_equity.db')
cursor = conn.cursor()

# Create Patients table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Patients (
        PatientID INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Gender TEXT,
        Ethnicity TEXT,
        Address TEXT,
        City TEXT,
        State TEXT,
        ZipCode TEXT,
        Phone TEXT,
        Email TEXT,
        LanguagePreference TEXT,
        SocioeconomicStatus TEXT,
        SpecialNeeds TEXT
    )
''')

# Create HealthcareProviders table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS HealthcareProviders (
        ProviderID INTEGER PRIMARY KEY,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        Specialty TEXT,
        HospitalAffiliation TEXT,
        Address TEXT,
        City TEXT,
        State TEXT,
        ZipCode TEXT,
        Phone TEXT,
        Email TEXT
    )
''')

# Create Appointments table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Appointments (
        AppointmentID INTEGER PRIMARY KEY,
        PatientID INTEGER,
        ProviderID INTEGER,
        AppointmentDate TEXT,
        AppointmentTime TEXT,
        Status TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
        FOREIGN KEY (ProviderID) REFERENCES HealthcareProviders(ProviderID)
    )
''')

# Insert 20 records into Patients table
for _ in range(20):
    data = generate_realistic_data()
    cursor.execute("INSERT INTO Patients (FirstName, LastName, Gender, Ethnicity, Address, City, State, ZipCode, Phone, Email, LanguagePreference, SocioeconomicStatus, SpecialNeeds) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

# Insert 20 records into HealthcareProviders table
for _ in range(20):
    first_name = fake.first_name()
    last_name = fake.last_name()
    specialty = fake.random_element(["Cardiology", "Pediatrics", "Orthopedics", "Dermatology", "Ophthalmology", "Neurology"])
    hospital_affiliation = fake.random_element(["General Hospital", "Children's Hospital", "University Hospital", "Specialty Clinic"])
    address = fake.street_address()
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()
    phone = fake.phone_number()
    email = fake.email()
    cursor.execute("INSERT INTO HealthcareProviders (FirstName, LastName, Specialty, HospitalAffiliation, Address, City, State, ZipCode, Phone, Email) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (first_name, last_name, specialty, hospital_affiliation, address, city, state, zip_code, phone, email))

# Insert 20 records into Appointments table
for _ in range(20):
    patient_id = fake.random_int(min=1, max=20)
    provider_id = fake.random_int(min=1, max=20)
    appointment_date = fake.date_this_year().strftime('%Y-%m-%d')
    appointment_time = fake.time(pattern='%H:%M')
    status = fake.random_element(["Scheduled", "Canceled", "Completed"])
    cursor.execute("INSERT INTO Appointments (PatientID, ProviderID, AppointmentDate, AppointmentTime, Status) VALUES (?, ?, ?, ?, ?)",
                   (patient_id, provider_id, appointment_date, appointment_time, status))

# Commit the changes
conn.commit()

# Close connection
conn.close()
