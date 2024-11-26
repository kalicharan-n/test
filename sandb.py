import sqlite3

def create_sample_db():
    conn = sqlite3.connect('sample.db')
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            from_date TEXT NOT NULL,
            to_date TEXT NOT NULL
        )
    ''')

    # Insert sample data
    sample_data = [
        ('Alice', '2023-01-01', '2023-12-31'),
        ('Bob', '2023-05-01', '2023-10-31'),
        ('Charlie', '2023-02-15', '2023-08-20'),
        ('Diana', '2024-01-01', '2024-12-31'),
    ]
    cursor.executemany('''
        INSERT INTO members (name, from_date, to_date) VALUES (?, ?, ?)
    ''', sample_data)

    conn.commit()
    conn.close()

# Call the function to create the database
create_sample_db()
