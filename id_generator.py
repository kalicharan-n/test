# id_generator.py

import sqlite3

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
