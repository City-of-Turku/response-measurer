import csv
import sqlite3
import datetime
import shutil
from pathlib import Path

from utils import load_settings


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
    

def copy_file_to_destination(filename: str, destination_folder: str) -> None:
    source_file = Path.cwd() / filename
    destination_file = Path(destination_folder) / filename
    shutil.copy(str(source_file), str(destination_file))


if __name__ == "__main__":
    settings = load_settings('settings.json')
    destination_folder = settings.get('destination_folder')
    conn = sqlite3.connect('response_times.db')
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f'measurements_{current_date}.csv'
    export_unexported_data(conn, filename)
    if destination_folder:
        copy_file_to_destination(filename, destination_folder)