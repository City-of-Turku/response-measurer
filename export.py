import csv
import sqlite3
import datetime


def export_unexported_data(conn: sqlite3.Connection, filename: str) -> None:
    cursor = conn.cursor()
    cursor.execute('SELECT id, timestamp, response_time_ms, payload_bytes, is_up FROM response_times WHERE exported = 0')

    data = cursor.fetchall()

    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['id', 'timestamp', 'response_time_ms', 'payload_bytes', 'is_up'])
        csv_writer.writerows(data)
    
    for measurement in data:
        cursor.execute("UPDATE response_times SET exported = 1 WHERE id = ?", (measurement[0],))
    
    conn.commit()
    

if __name__ == "__main__":
    conn = sqlite3.connect('response_times.db')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f'measurements_{current_date}.csv'
    export_unexported_data(conn, filename)