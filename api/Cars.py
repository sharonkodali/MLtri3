from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect('ford_models.db')
    return conn

@app.route('/create_table', methods=['GET'])
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            year INTEGER NOT NULL,
            engine TEXT NOT NULL,
            trim TEXT NOT NULL,
            price REAL NOT NULL,
            horsepower INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    return "Table created successfully"

@app.route('/populate_data', methods=['GET'])
def populate_data():
    car_data = [
        ('Mustang', 2023, 'V8', 'GT', 55000.0, 450),
        ('F-150', 2022, 'V6', 'XLT', 45000.0, 400),
        ('Escape', 2021, 'I4', 'Titanium', 35000.0, 250),
        ('Explorer', 2023, 'V6', 'Limited', 50000.0, 365),
        ('Bronco', 2023, 'I4', 'Base', 35000.0, 300),
        ('Escape', 2024, 'I4', 'Base', 29345.0, 180)  # New 2024 Ford Escape data
    ]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO car_models (model_name, year, engine, trim, price, horsepower)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', car_data)
    conn.commit()
    conn.close()
    return "Data populated successfully"

@app.route('/cars', methods=['GET'])
def get_cars():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM car_models')
    rows = cursor.fetchall()
    conn.close()
    cars = []
    for row in rows:
        cars.append({
            'id': row[0],
            'model_name': row[1],
            'year': row[2],
            'engine': row[3],
            'trim': row[4],
            'price': row[5],
            'horsepower': row[6]
        })
    return jsonify(cars)

if __name__ == '__main__':
    app.run(debug=True)
