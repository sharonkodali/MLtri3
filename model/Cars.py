from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import logging
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

DATABASE = 'car_models.db'

# Configure logging
logging.basicConfig(level=logging.INFO)

def connect_db():
    conn = sqlite3.connect(DATABASE, timeout=10)  # Increased timeout
    return conn

@app.route('/create_tables', methods=['GET'])
def create_tables():
    logging.info("Creating tables...")
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('DROP TABLE IF EXISTS ford_models')
            cursor.execute('DROP TABLE IF EXISTS bmw_models')
            cursor.execute('DROP TABLE IF EXISTS honda_models')

            cursor.execute('''
                CREATE TABLE ford_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    price REAL NOT NULL,
                    horsepower INTEGER NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE bmw_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    price REAL NOT NULL,
                    horsepower INTEGER NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE honda_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    price REAL NOT NULL,
                    horsepower INTEGER NOT NULL
                )
            ''')
            conn.commit()
            logging.info("Tables created successfully")

            # Verify tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ford_models'")
            if cursor.fetchone():
                logging.info("Table 'ford_models' exists.")
            else:
                logging.error("Table 'ford_models' does not exist.")

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bmw_models'")
            if cursor.fetchone():
                logging.info("Table 'bmw_models' exists.")
            else:
                logging.error("Table 'bmw_models' does not exist.")

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='honda_models'")
            if cursor.fetchone():
                logging.info("Table 'honda_models' exists.")
            else:
                logging.error("Table 'honda_models' does not exist.")

            return "Tables created successfully"
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")
            return f"Error creating tables: {e}", 500

@app.route('/populate_data/<brand>', methods=['GET'])
def populate_data(brand):
    car_data = {
        'ford': [
            ('Mustang', 2023, 57945.0, 450),
            ('F-150', 2022, 33315.0, 290),
            ('Escape', 2021, 26800.0, 250),
            ('Explorer', 2023, 36760.0, 300),
            ('Bronco', 2023, 35000.0, 300),
            ('Escape', 2024, 29495.0, 250)
        ],
        'bmw': [
            ('X5', 2023, 60000.0, 450),
            ('M3', 2022, 70000.0, 473),
            ('i8', 2021, 140000.0, 369),
            ('X3', 2023, 43000.0, 382),
            ('M5', 2023, 103500.0, 617),
            ('Z4', 2024, 50000.0, 255)
        ],
        'honda': [
            ('Civic', 2023, 23000.0, 158),
            ('Accord', 2022, 28000.0, 192),
            ('CR-V', 2021, 25000.0, 190),
            ('Pilot', 2023, 37000.0, 280),
            ('Odyssey', 2023, 35000.0, 280),
            ('Fit', 2024, 17000.0, 130)
        ]
    }
    
    if brand not in car_data:
        logging.error(f"Brand {brand} not supported")
        return "Brand not supported", 400

    table_name = f"{brand}_models"
    data = car_data[brand]

    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f'DELETE FROM {table_name}')  # Clear existing data to prevent duplicates
            cursor.executemany(f'''
                INSERT INTO {table_name} (model_name, year, price, horsepower)
                VALUES (?, ?, ?, ?)
            ''', data)
            conn.commit()
            logging.info(f"Data populated successfully for {brand}")

            # Verify data insertion
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            logging.info(f"Inserted {count} rows into {table_name}")

            return "Data populated successfully"
        except sqlite3.OperationalError as e:
            logging.error(f"Error populating data for {brand}: {e}")
            return f"Error populating data for {brand}: {e}", 500

@app.route('/cars/<brand>', methods=['GET'])
def get_cars(brand):
    table_name = f"{brand}_models"
    cars = []
    
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f'SELECT * FROM {table_name}')
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    cars.append({
                        'id': row[0],
                        'model_name': row[1],
                        'year': row[2],
                        'price': row[3],
                        'horsepower': row[4]
                    })
                logging.info(f"Retrieved data for {brand}: {json.dumps(cars, indent=4)}")
                return jsonify(cars)
            else:
                logging.warning(f"No data found for {brand}")
                return jsonify(cars)
        except sqlite3.OperationalError as e:
            logging.error(f"Error retrieving data for {brand}: {e}")
            return f"Error retrieving data for {brand}: {e}", 500

@app.route('/sort_cars/<brand>', methods=['GET'])
def sort_cars(brand):
    sort_by = request.args.get('sort_by', 'price')  # Default to sorting by price
    order = request.args.get('order', 'asc')  # Default to ascending order
    table_name = f"{brand}_models"

    cars = []
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            if order == 'asc':
                cursor.execute(f'SELECT * FROM {table_name} ORDER BY {sort_by} ASC')
            else:
                cursor.execute(f'SELECT * FROM {table_name} ORDER BY {sort_by} DESC')
            rows = cursor.fetchall()
            for row in rows:
                cars.append({
                    'id': row[0],
                    'model_name': row[1],
                    'year': row[2],
                    'price': row[3],
                    'horsepower': row[4]
                })
            logging.info(f"Sorted data for {brand} by {sort_by} in {order} order: {json.dumps(cars, indent=4)}")
            return jsonify(cars)
        except sqlite3.OperationalError as e:
            logging.error(f"Error sorting data for {brand}: {e}")
            return f"Error sorting data for {brand}: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
