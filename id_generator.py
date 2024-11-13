# id_generator.py

import random
import sqlite3
from flask import g


# Function to get the last generated ID
def get_last_id():
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute('SELECT last_id FROM ids WHERE name = ?', ('last_generated_id',))
    last_id = cursor.fetchone()[0]
    conn.close()
    return last_id

# Function to update the last generated ID
def update_last_id(new_id):
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE ids SET last_id = ? WHERE name = ?', (new_id, 'last_generated_id'))
    conn.commit()
    conn.close()

# Custom incrementing ID function
def incrementing_id():
    last_id = get_last_id()
    new_id = last_id + 1
    update_last_id(new_id)
    return str(new_id)

# Function to get the database connection
def get_plan_db():
    DATABASE = 'health_plans.db'
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_plan_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
        
# Class to manage health plan information
class HealthPlan:
    def __init__(self, plan_id, sub_plan_id):
        self.plan_id = plan_id
        self.sub_plan_id = sub_plan_id
        # Initialize instance variables to store values
        self.state = None
        self.county_code = None
        self.county_name = None
        self.city = None
        self.zip_code = None

        # Fetch all the data for the given plan_id and sub_plan_id in a single query
        self._fetch_all_data()

    # Function to fetch all data (state, county, zip, etc.) in a single query
    def _fetch_all_data(self):
        # SQL query to fetch all the required fields from the database for the given plan_id and sub_plan_id
        query = """
        SELECT state, county_code, county_name, city, zip_code
        FROM plans
        WHERE plan_id = ? AND sub_plan_id = ?
        """

        # # Get the database connection
        # conn = get_plan_db()
        with sqlite3.connect('health_plans.db') as conn:
        # Execute the query with the plan_id and sub_plan_id
            cursor = conn.execute(query, (self.plan_id, self.sub_plan_id))
            result = cursor.fetchall()
            #result = cursor.fetchone()
        
        # Close the connection
        # conn.close()

        # If the result exists, store the values in the instance variables
        if result:
            result = random.choice(result)
            print(result)
            self.state, self.county_code, self.county_name, self.city, self.zip_code = result
            # self.state, self.county_code, self.county_name, self.city, self.zip_code = random.choice(result)
            # print(self.state, self.county_code, self.county_name, self.city, self.zip_code)
        else:
            # Handle case where no result was found (optional)
            self.state = self.county_code = self.county_name = self.city = self.zip_code = None
    # Getter methods to access each field
    def get_state(self):
        return self.state

    def get_county_code(self):
        return self.county_code

    def get_county_name(self):
        return self.county_name

    def get_city(self):
        return self.city

    def get_zip_code(self):
        return self.zip_code