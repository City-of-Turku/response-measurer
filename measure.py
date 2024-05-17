import pyodbc
import time
import sqlite3
import json
import sys


def load_settings(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        settings = json.load(file)
    return settings


def create_table_if_not_exists(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            unix_timestamp INT,
            response_time_ms REAL,
            payload_bytes INT,
            is_up BOOLEAN
        )
    ''')
    conn.commit()


def insert_result_to_db(
    conn: sqlite3.Connection,
    timestamp: str,
    unix_timestamp: int,
    response_time_ms: float,
    payload_bytes: int,
    is_up: bool
) -> None:
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO response_times (timestamp, unix_timestamp, response_time_ms, payload_bytes, is_up)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, unix_timestamp, response_time_ms, payload_bytes, is_up))
    conn.commit()


def connect_and_query(settings: dict) -> int:
    username = settings.get('username')
    password = settings.get('password')
    server = settings.get('server')
    database = settings.get('database')
    driver = settings.get('driver')
    table = settings.get('table')
    if username and password:
        connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
    else:
        connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes'
    
    try:
        conn = pyodbc.connect(connection_string)

        cursor = conn.cursor()
        query = f'SELECT TOP 10 * FROM {table} ORDER BY NEWID();'
        cursor.execute(query)

        total_size = 0
        for row in cursor.fetchall():
            row_size = sum(sys.getsizeof(col) for col in row)
            total_size += row_size

        return total_size
    
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return 0
    
    finally:
        cursor.close()
        conn.close()


def measure_and_store_response_time(settings: dict, conn: sqlite3.Connection):
    start_time = time.time()
    result_bytes = connect_and_query(settings)
    end_time = time.time()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    timestamp_struct = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    unix_timestamp = time.mktime(timestamp_struct)
    response_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
    is_up = True if result_bytes else False
    print(f"Response time: {response_time_ms:.2f} ms, payload {result_bytes} bytes")
    insert_result_to_db(conn, timestamp, unix_timestamp, response_time_ms, result_bytes, is_up)


def main() -> None:
    settings = load_settings('settings.json')
    conn = sqlite3.connect('response_times.db')
    create_table_if_not_exists(conn)
    measure_and_store_response_time(settings, conn)
    conn.close()


if __name__ == "__main__":
    main()