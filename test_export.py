import csv
import sqlite3
from datetime import datetime

import os

from export import copy_file_to_destination
from utils import load_settings

def handle_export(c, destination_folder):
    c.execute('SELECT * FROM response_times')
    row = c.fetchone()
    if row:
        column_names = [description[0] for description in c.description]
        timestamp = datetime.fromtimestamp(row[column_names.index('unix_timestamp')])

        row_data = [
            row[column_names.index('id')],
            timestamp.isoformat(),
            row[column_names.index('response_time_ms')],
            row[column_names.index('payload_bytes')],
            row[column_names.index('is_up')]
        ]

        filename = 'test_report.csv'
        reports_folder = 'reports'
        os.makedirs(reports_folder, exist_ok=True)
        file_path = os.path.join(reports_folder, filename)
        with open(file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['id', 'timestamp', 'response_time_ms', 'payload_bytes', 'is_up'])
            csvwriter.writerow(row_data)

        print('Test export CSV created successfully.')
        if destination_folder:
            print(f'Attempting to copy test export to {destination_folder}.')
            copy_file_to_destination(file_path, destination_folder)
            
        else:
            print('No destination folder specified in settings. Skipping copying.')
    else:
        print('No rows found.')


if __name__ == "__main__":
    settings = load_settings('settings.json')
    destination_folder = settings.get('destination_folder')
    conn = sqlite3.connect('response_times.db')
    c = conn.cursor()
    handle_export(c, destination_folder)
    print('Test done.')
    print('Press any key to exit...')
    input()