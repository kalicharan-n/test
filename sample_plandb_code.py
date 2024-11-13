import sqlite3
import random

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('health_plans.db')
cursor = conn.cursor()

# Create a table to store plan information
cursor.execute('''
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT,
    sub_plan_id TEXT,
    state TEXT,
    county_code TEXT,
    county_name TEXT,
    city TEXT,
    zip_code TEXT
)
''')

# Sample data for states, counties, and cities
states = ['NY', 'CA', 'TX', 'FL', 'IL']
counties = [
    ('001', 'Albany County'), ('003', 'Bronx County'), 
    ('005', 'Kings County'), ('007', 'Queens County'), 
    ('009', 'Orange County')
]
cities = ['Albany', 'Bronx', 'Brooklyn', 'Queens', 'Orlando']
zip_codes = ['10001', '10002', '10003', '10004', '10005']

# Function to generate a random plan and sub-plan ID
def generate_plan_ids(plan_number):
    return f"PLAN{plan_number:03}", f"SUB{plan_number:03}"

# Insert sample data for 10 plans with multiple counties and zip codes
for plan_number in range(1, 11):  # 10 plans
    plan_id, sub_plan_id = generate_plan_ids(plan_number)
    state = random.choice(states)
    
    for county_code, county_name in counties:
        city = random.choice(cities)
        
        # Assign multiple zip codes to each county
        for _ in range(random.randint(2, 4)):  # Each county has 2-4 zip codes
            zip_code = random.choice(zip_codes)
            cursor.execute('''
                INSERT INTO plans (plan_id, sub_plan_id, state, county_code, county_name, city, zip_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (plan_id, sub_plan_id, state, county_code, county_name, city, zip_code))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and sample records created successfully.")
