import pyodbc
import time
import sqlite3
import requests
import pickle
import keyring

from driver import Driver
from utils import load_settings, logger


def create_table_if_not_exists(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS response_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            unix_timestamp INT,
            response_time_ms REAL,
            payload_bytes INT,
            is_up BOOLEAN,
            exported BOOLEAN
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
        INSERT INTO response_times (timestamp, unix_timestamp, response_time_ms, payload_bytes, is_up, exported)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, unix_timestamp, response_time_ms, payload_bytes, is_up, False))
    conn.commit()


def connect_and_query(settings: dict) -> int:
    username = settings.get('username')
    password = keyring.get_password('response-measurer', username)
    server = settings.get('server')
    port = settings.get('port', 1433)
    database = settings.get('database')
    driver = Driver(settings.get('driver'))
    table = settings.get('table')
    if username and password:
        connection_string = f'DRIVER={driver.driver_str};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password}'
    else:
        connection_string = f'DRIVER={driver.driver_str};SERVER={server};PORT={port};DATABASE={database};Trusted_Connection=yes'
    
    try:
        conn = pyodbc.connect(connection_string)

        cursor = conn.cursor()
        query = driver.get_query_str(table)

        cursor.execute(query)

        total_size = 0
        for row in cursor.fetchall():
            total_size += len(pickle.dumps(row))

        return total_size
    
    except pyodbc.Error as e:
        logger.error(f"Error: {e}")
        return 0
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def is_network_connection_working(network_test_addr: str) -> bool:
    if not network_test_addr:
        return True
    try:
        logger.info('Testing for network issues...')
        requests.get(network_test_addr, timeout=30)
        logger.info('Network looks ok')
        return True
    except Exception as e:
        logger.error('Network error:', e)
        return False


def measure_and_store_response_time(settings: dict, conn: sqlite3.Connection) -> None:
    start_time = time.time()
    result_bytes = connect_and_query(settings)

    if not result_bytes and not is_network_connection_working(settings.get('network_test_addr')):
        logger.info("Skipping measurement storing due to network issue.")
        return

    end_time = time.time()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Current timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    timestamp_struct = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    unix_timestamp = time.mktime(timestamp_struct)
    response_time_ms = (end_time - start_time) * 1000  # Convert to milliseconds
    is_up = True if result_bytes else False
    logger.info(f"Response time: {response_time_ms:.2f} ms, payload {result_bytes} bytes")
    insert_result_to_db(conn, timestamp, unix_timestamp, response_time_ms, result_bytes, is_up)


def main() -> None:
    settings = load_settings('settings.json')
    conn = sqlite3.connect('response_times.db')
    create_table_if_not_exists(conn)
    measure_and_store_response_time(settings, conn)
    conn.close()


if __name__ == "__main__":
    main()