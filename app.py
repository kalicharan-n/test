from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from faker import Faker
import re

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'template_files'
fake = Faker()

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the database for storing the last ID
def initialize_db():
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ids (name TEXT PRIMARY KEY, last_id INTEGER)''')
    cursor.execute('INSERT OR IGNORE INTO ids (name, last_id) VALUES (?, ?)', ('last_generated_id', 0))
    conn.commit()
    conn.close()

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

# Placeholder mappings
fake_methods = {
    'street_address': fake.street_address,
    'first_name': fake.first_name,
    'incrementing_id': incrementing_id
}

# Data generation function
def generate_data(template_file, num_records=10):
    with open(template_file, 'r') as file:
        lines = file.readlines()

    generated_data = []
    for _ in range(num_records):
        record = []
        for line in lines:
            placeholders = re.findall(r'\{(\w+)\}', line)
            for placeholder in placeholders:
                if placeholder in fake_methods:
                    line = line.replace(f'{{{placeholder}}}', fake_methods[placeholder]())
            record.append(line.strip())
        # generated_data.append("\n".join(record))
        generated_data.append("\n".join(record))
    return generated_data

# Initialize the database
initialize_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    layouts = os.listdir(app.config['UPLOAD_FOLDER'])
    generated_data = []
    num_records = 1  # Default value

    if request.method == 'POST':
        num_records = int(request.form.get('num_records', 1))
        selected_layout = request.form.get('layout')
        template_file = os.path.join(app.config['UPLOAD_FOLDER'], selected_layout)
        generated_data = generate_data(template_file, num_records)

    return render_template('index.html', generated_data=generated_data, layouts=layouts, num_records=num_records)


# Route for the Enroll Data page
@app.route('/enroll_data', methods=['GET', 'POST'])
def enroll_data():
    if request.method == 'POST':
        # Process enrollment data here
        contract = request.form.get('contract')
        subc = request.form.get('subc')
        effective_date = request.form.get('effective_date')
        state = request.form.get('state')
        # Add data processing or save logic here

    return render_template('enroll_data.html')

@app.route('/layouts', methods=['GET', 'POST'])
def layouts():
    if request.method == 'POST':
        # Add new layout with freeform text
        layout_name = request.form.get('layout_name').strip()
        layout_content = request.form.get('layout_content').strip()
        
        if layout_name and layout_content:
            layout_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{layout_name}.txt")
            with open(layout_path, 'w', newline="") as layout_file:
                layout_file.write(layout_content)
            flash(f"Layout '{layout_name}' added successfully.")
            return redirect(url_for('layouts'))
        else:
            flash("Please enter both a layout name and content.")
    
    layouts = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('layouts.html', layouts=layouts)

@app.route('/layouts/delete/<filename>')
def delete_layout(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Layout '{filename}' deleted successfully.")
    return redirect(url_for('layouts'))

@app.route('/layouts/edit/<filename>', methods=['GET', 'POST'])
def edit_layout(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if request.method == 'POST':
        content = request.form['content']
        with open(filepath, 'w', newline='') as f:
            f.write(content)
        flash(f"Layout '{filename}' updated successfully.")
        return redirect(url_for('layouts'))

    with open(filepath, 'r') as f:
        content = f.read().strip()
    return render_template('edit_layout.html', filename=filename, content=content)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Fetch all ID field names (from the 'name' column in 'ids' table)
    id_fields = get_id_fields()

    # Default current ID to display
    current_id = get_current_id(id_fields[0]) if id_fields else 0

    if request.method == 'POST':
        selected_id_field = request.form.get('id_field')
        reset_type = request.form.get('reset_type')  # Type of reset (e.g., 'increment' or 'reset')

        if selected_id_field:
            # Handle resetting or incrementing the ID field
            if reset_type == 'increment':
                increment_id(selected_id_field)
            elif reset_type == 'reset':
                new_id = request.form.get('new_id')
                if new_id and new_id.isdigit():
                    new_id = int(new_id)
                    reset_id(selected_id_field, new_id)  # Pass the new ID value to reset
                else:
                    flash("Please enter a valid ID.")

            flash(f"ID field '{selected_id_field}' has been successfully updated.")
            current_id = get_current_id(selected_id_field)  # Get the new current ID after reset

    return render_template('admin.html', id_fields=id_fields, current_id=current_id)


def get_id_fields():
    # Fetch all column names for the id fields dynamically
    query = "SELECT name FROM ids"
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    result=cursor.execute(query).fetchall()
    print(result)
    # Extract column names excluding the primary key column
    return [row[0] for row in result]

def get_current_id(id_field):
    # Fetch the current ID from the database for the selected ID field
    query = f"SELECT last_id FROM ids WHERE name = ?"
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    result = cursor.execute(query, (id_field,)).fetchone()
    return result[0] if result else 0

def increment_id(id_field):
    # Increment the ID field value in the database
    query = f"UPDATE ids SET last_id = last_id + 1 WHERE name = ?"
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute(query, (id_field,))
    conn.commit()

def reset_id(id_field,new_id):
    # Reset the ID field value in the database (set to 1 or a default value)
    query = f"UPDATE ids SET last_id = ? WHERE name = ?"
    conn = sqlite3.connect('id_storage.db')
    cursor = conn.cursor()
    cursor.execute(query, (new_id, id_field))
    conn.commit()


if __name__ == '__main__':
    app.run(debug=True)
