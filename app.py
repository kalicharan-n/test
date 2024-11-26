import sys
from flask import Flask, Response, json, jsonify, render_template, request, redirect, url_for, flash
import sqlite3
import os
from faker import Faker
import re
from placeholders import fake_methods
from id_generator import get_plan_db, close_plan_connection, HealthPlan
import time
import threading
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# # Register the teardown function for closing DB connection
# app.teardown_appcontext(close_plan_connection)

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

def create_table():
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            service_name TEXT,
            parameter_key TEXT,
            parameter_value TEXT,
            PRIMARY KEY (service_name, parameter_key)
        )
    ''')
    connection.commit()
    connection.close()
    
def add_credential(service_name, username, password):
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO credentials (service_name, username, password_hash) VALUES (?, ?, ?)',
                       (service_name, username, hashed_password))
        connection.commit()
    except sqlite3.IntegrityError:
        return "Service already exists."
    finally:
        connection.close()

def update_credential(service_name, new_password):
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    hashed_password = generate_password_hash(new_password)
    cursor.execute('UPDATE credentials SET password_hash = ? WHERE service_name = ?', (hashed_password, service_name))
    connection.commit()
    connection.close()

def fetch_credentials():
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    cursor.execute('SELECT service_name, username FROM credentials')
    credentials = cursor.fetchall()
    connection.close()
    return credentials

def delete_credential(service_name):
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM credentials WHERE service_name = ?', (service_name,))
    connection.commit()
    connection.close()

def add_or_update_service(service_name, parameters):
    """
    Adds or updates a service configuration in the database.
    Parameters is a dictionary containing key-value pairs for the service.
    """
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    for key, value in parameters.items():
        if key == "password":  # Hash the password
            value = generate_password_hash(value)
        cursor.execute('''
            INSERT INTO credentials (service_name, parameter_key, parameter_value)
            VALUES (?, ?, ?)
            ON CONFLICT(service_name, parameter_key) DO UPDATE SET parameter_value = excluded.parameter_value
        ''', (service_name, key, value))
    connection.commit()
    connection.close()

def fetch_service_configuration(service_name):
    """
    Fetches all parameters for a given service.
    """
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    cursor.execute('SELECT parameter_key, parameter_value FROM credentials WHERE service_name = ?', (service_name,))
    parameters = cursor.fetchall()
    connection.close()
    return {key: value for key, value in parameters}

def delete_service(service_name):
    """
    Deletes all parameters for a given service.
    """
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM credentials WHERE service_name = ?', (service_name,))
    connection.commit()
    connection.close()


# # Function to get the last generated ID
# def get_last_id():
#     conn = sqlite3.connect('id_storage.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT last_id FROM ids WHERE name = ?', ('last_generated_id',))
#     last_id = cursor.fetchone()[0]
#     conn.close()
#     return last_id

# # Function to update the last generated ID
# def update_last_id(new_id):
#     conn = sqlite3.connect('id_storage.db')
#     cursor = conn.cursor()
#     cursor.execute('UPDATE ids SET last_id = ? WHERE name = ?', (new_id, 'last_generated_id'))
#     conn.commit()
#     conn.close()

# # Custom incrementing ID function
# def incrementing_id():
#     last_id = get_last_id()
#     new_id = last_id + 1
#     update_last_id(new_id)
#     return str(new_id)

# # Placeholder mappings
# fake_methods = {
#     'street_address': fake.street_address,
#     'first_name': fake.first_name,
#     'incrementing_id': incrementing_id
# }

# Data generation function
# Data generation function
# Global progress dictionary
progress_data = {"processed": 0, "total": 0}

def generate_data(template_file, num_records=10, enroll_data=False, plan_id="",sub_plan_id=""):
    global progress_data
    with open(template_file, 'r') as file:
        lines = file.readlines()

    progress_data["total"] = num_records
    progress_data["processed"] = 0
    generated_data = []

    for _ in range(num_records):
        if enroll_data==True:
            print("enrollment functions")
            health_plan = HealthPlan(plan_id, sub_plan_id)
            fake_methods['healthplan_city'] = {
                "method": health_plan.get_city,
                "example": "city name"
            }
            fake_methods['healthplan_county'] = {
                "method": health_plan.get_county_code,
                "example": "city name"
            }
            fake_methods['healthplan_zip'] = {
                "method": health_plan.get_zip_code,
                "example": "city name"
            }
            fake_methods['healthplan_state'] = {
                "method": health_plan.get_state,
                "example": "city name"
            }         
        record = []
        for line in lines:
            placeholders = re.findall(r'\{(\w+)\}', line)
            for placeholder in placeholders:
                if placeholder in fake_methods:
                    # Replace the placeholder with the method-generated value
                    # print(f'for a placeholder {placeholder} method is {fake_methods[placeholder]["method"]}')
                    # print(f"value is {health_plan.get_city()}")
                    line = line.replace(f'{{{placeholder}}}', str(fake_methods[placeholder]["method"]()))
            record.append(line.strip())

        generated_data.append("\n".join(record))
        progress_data["processed"] += 1  # Update processed count
        yield f"data: {json.dumps(progress_data)}\n\n"  # Send progress update

    return generated_data

# Initialize the database
initialize_db()
create_table()

@app.route('/generate_progress', methods=['GET'])
def generate_progress():
    # def stream():
    #     global progress_data
    #     while progress_data["processed"] < progress_data["total"]:
    #         yield f"data: {json.dumps(progress_data)}\n\n"
    #         time.sleep(0.5)  # Adjust interval as needed
    #     yield f"data: {json.dumps(progress_data)}\n\n"

    return Response(generate_data(num_records), content_type='text/event-stream')

@app.route('/', methods=['GET', 'POST'])
def index():
    layouts = os.listdir(app.config['UPLOAD_FOLDER'])
    generated_data = []
    num_records = 1  # Default value

    if request.method == 'POST':
        num_records = int(request.form.get('num_records', 1))
        selected_layout = request.form.get('layout')
        template_file = os.path.join(app.config['UPLOAD_FOLDER'], selected_layout)
        generated_data = generate_data(template_file, num_records, False)

    return render_template('index.html', generated_data=generated_data, layouts=layouts, num_records=num_records)


# Route for the Enroll Data page
@app.route('/enroll_data', methods=['GET', 'POST'])
def enroll_data():
    # Query to fetch distinct plan_ids (contracts)
    conn = get_plan_db()
    cursor = conn.execute("SELECT DISTINCT plan_id FROM plans")
    contracts = cursor.fetchall()  # Fetch all unique contracts
    
    if request.method == 'POST':
        # Process enrollment data here
        num_records = int(request.form.get('num_records', 1))
        selected_layout = "testlayout.txt"
        template_file = os.path.join(app.config['UPLOAD_FOLDER'], selected_layout)
        contract = request.form.get('contract')
        subc = request.form.get('subc')
        effective_date = request.form.get('effective_date')
        state = request.form.get('state')
        # Add data processing or save logic here
        print(contract)
        generated_data = generate_data(template_file, num_records, True,contract,subc)
        return render_template('enroll_data.html',generated_data=generated_data,num_records=num_records,contracts=contracts)
    
     # Render the index page with the contracts dropdown
    return render_template('enroll_data.html', contracts=contracts)

@app.route('/get_sub_plan_ids', methods=['GET'])
def get_sub_plan_ids():
    # Get the plan_id from the query parameter
    plan_id = request.args.get('plan_id')
    
    if plan_id:
        conn = get_plan_db()
        cursor = conn.execute("SELECT DISTINCT sub_plan_id FROM plans WHERE plan_id = ?", (plan_id,))
        sub_plans = cursor.fetchall()
        
        # Return the result as a JSON response
        return jsonify([sub_plan[0] for sub_plan in sub_plans])
    return jsonify([])  # Return an empty list if no plan_id is provided


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
    return render_template(
        'layouts.html', 
        layouts=layouts, 
        placeholders=fake_methods  # Pass the placeholders with examples
    )

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

    # # Pass the fake methods keys to the template as 'placeholders'
    # placeholders = list(fake_methods.keys())

    return render_template('edit_layout.html', filename=filename, content=content, placeholders=fake_methods)

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
                    flash('ID value updated successfully!', 'success')
                else:
                    flash("Please enter a valid ID.")

            flash(f"ID field {selected_id_field} has been successfully updated.")
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
# Testing sample code starts here

# Task statuses (shared state for simplicity)
task_status = [
    {"task": "FTP File Transfer", "status": "Pending"},
    {"task": "Run Shell Script 1", "status": "Pending"},
    {"task": "Run Shell Script 2", "status": "Pending"},
    {"task": "Run Shell Script 3", "status": "Pending"},
    {"task": "Run Shell Script 4", "status": "Pending"}
]

def run_tasks(generated_data):
    """Simulate background tasks."""
    global task_status
    task_status[0]["status"] = "In Progress"
    print(generated_data)
    time.sleep(2)  # Simulate FTP transfer
    task_status[0]["status"] = "Completed"

    task_status[1]["status"] = "In Progress"
    time.sleep(3)  # Simulate shell script 1
    task_status[1]["status"] = "Completed"

    task_status[2]["status"] = "In Progress"
    time.sleep(1)  # Simulate shell script 2
    task_status[2]["status"] = "Completed"
    
    task_status[3]["status"] = "In Progress"
    time.sleep(1)  # Simulate shell script 2
    task_status[3]["status"] = "Completed"

    task_status[4]["status"] = "In Progress"
    time.sleep(1)  # Simulate shell script 2
    task_status[4]["status"] = "Completed"
    

@app.route('/push_status_sse', methods=['GET'])
def push_status_sse():
    """SSE endpoint to stream task status updates."""
    def generate():
        global task_status
        while True:
            yield f"data: {json.dumps(task_status)}\n\n"
            sys.stdout.flush()
            if all(task["status"] == "Completed" for task in task_status):
                break
            time.sleep(1)

    return Response(generate(), content_type='text/event-stream')

@app.route('/start_push', methods=['POST'])
def start_push():
    global task_status
    data = request.get_json()
    generated_data = data.get("generated_data")
    # print("Received generated data:", generated_data)
    # Reset task statuses
    for task in task_status:
        task["status"] = "Pending"

    # Run tasks in a background thread
    threading.Thread(target=run_tasks,args=(generated_data,)).start()
    return '', 204



@app.route('/system_settings/delete_credential', methods=['POST'])
def delete_credential_route():
    service_name = request.form['service_name']
    delete_credential(service_name)
    flash("Credential deleted successfully.")
    return redirect('/system_settings')

@app.route('/system_settings/add_or_update_service', methods=['POST'])
def add_or_update_service_route():
    service_name = request.form['service_name']
    parameters = {
        "host": request.form.get('host'),
        "port": request.form.get('port'),
        "username": request.form.get('username'),
        "password": request.form.get('password'),
    }
    # Add more parameters dynamically from the form
    for key, value in request.form.items():
        if key not in parameters and key != 'service_name':
            parameters[key] = value
    add_or_update_service(service_name, parameters)
    flash("Service configuration saved successfully.")
    return redirect('/system_settings')

@app.route('/system_settings/edit_service/<service_name>', methods=['GET', 'POST'])
def edit_service(service_name):
    if request.method == 'POST':
        # Collect updated parameters from the form
        parameters = {
            "host": request.form.get('host'),
            "port": request.form.get('port'),
            "username": request.form.get('username'),
            "password": request.form.get('password'),
        }
        # Add any additional dynamic parameters
        for key, value in request.form.items():
            if key not in parameters and key != 'service_name':
                parameters[key] = value
        add_or_update_service(service_name, parameters)
        flash(f"Service '{service_name}' updated successfully.")
        return redirect('/system_settings')
    else:
        # Fetch existing parameters for the service
        parameters = fetch_service_configuration(service_name)
        return render_template('edit_service.html', service_name=service_name, parameters=parameters)


@app.route('/system_settings', methods=['GET'])
def system_settings():
    connection = sqlite3.connect('credentials.db')
    cursor = connection.cursor()
    cursor.execute('SELECT DISTINCT service_name FROM credentials')
    services = [row[0] for row in cursor.fetchall()]
    connection.close()

    service_details = {service: fetch_service_configuration(service) for service in services}
    return render_template('system_settings.html', services=service_details)




# Data Search Page
@app.route('/data_search', methods=['GET', 'POST'])
def data_search():
    if request.method == 'POST':
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')

        # Query the database
        conn = sqlite3.connect('sample.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM members
            WHERE from_date >= ? AND to_date <= ?
        ''', (from_date, to_date))
        results = cursor.fetchall()
        conn.close()

        return render_template('data_search.html', results=results, from_date=from_date, to_date=to_date)
    return render_template('data_search.html', results=None)

# Download Search Results as CSV
@app.route('/download_csv', methods=['POST'])
def download_csv():
    results = request.form.getlist('results[]')
    if results:
        response = make_response()
        response.headers['Content-Disposition'] = 'attachment; filename=search_results.csv'
        response.headers['Content-Type'] = 'text/csv'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'From Date', 'To Date'])
        for row in results:
            writer.writerow(eval(row))  # Convert string back to tuple
        return response
    flash("No data available to download.")
    return redirect(url_for('data_search'))


if __name__ == '__main__':
    app.run(debug=True)
