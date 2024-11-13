import sqlite3
from faker import Faker
import re

# Initialize Faker
fake = Faker()

# Database setup for storing the last ID
def initialize_db():
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ids (name TEXT PRIMARY KEY, last_id INTEGER)''')
    # Insert initial value if it does not exist
    cursor.execute('INSERT OR IGNORE INTO ids (name, last_id) VALUES (?, ?)', ('last_generated_id', 0))
    conn.commit()
    conn.close()

# Function to get the last generated ID from the database
def get_last_id():
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute('SELECT last_id FROM ids WHERE name = ?', ('last_generated_id',))
    last_id = cursor.fetchone()[0]
    conn.close()
    return last_id

# Function to update the last generated ID in the database
def update_last_id(new_id):
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ids SET last_id = ? WHERE name = ?', (new_id, 'last_generated_id'))
    conn.commit()
    conn.close()

# Custom function to generate an incrementing ID
def incrementing_id():
    last_id = get_last_id()
    new_id = last_id + 1
    update_last_id(new_id)
    return str(new_id)

# Define a dictionary to map placeholders to Faker methods and custom functions
fake_methods = {
    'street_address': fake.street_address,
    'first_name': fake.first_name,
    'incrementing_id': incrementing_id  # Adding custom incrementing ID function here
}

# Function to generate data based on template
def generate_data(template_file, num_records=10):
    with open(template_file, 'r') as file:
        lines = file.readlines()

    generated_data = []

    # Generate multiple records
    for _ in range(num_records):
        record = []
        # Process each line in the template
        for line in lines:
            placeholders = re.findall(r'\{(\w+)\}', line)
            # Replace each placeholder with corresponding Faker or custom value
            for placeholder in placeholders:
                if placeholder in fake_methods:
                    line = line.replace(f'{{{placeholder}}}', fake_methods[placeholder]())
            record.append(line.strip())
        generated_data.append("\n".join(record) + "\n")  # Separate each record

    return generated_data

# Initialize the database (only needs to be done once)
#initialize_db()

# Example usage
template_file = 'template.ini'
data = generate_data(template_file, num_records=5)
for item in data:
    print(item)
