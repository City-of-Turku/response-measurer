import csv
import sqlite3
from datetime import datetime, timedelta
import shutil
from pathlib import Path
import os

from utils import load_settings


def get_first_unexported_timestamp(c: sqlite3.Cursor):
    c.execute('SELECT timestamp FROM response_times WHERE exported = 0 ORDER BY unix_timestamp ASC LIMIT 1')
    row = c.fetchone()
    return row[0] if row else None


def fetch_weekly_data(c: sqlite3.Cursor, start_timestamp: str) -> list:
    start_date = datetime.strptime(start_timestamp, '%Y-%m-%d %H:%M:%S')
    zeroed_start_date = start_date.replace(hour=0, minute=0, second=0)
    zeroed_start_timestamp = zeroed_start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date = zeroed_start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
    end_timestamp = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''
        SELECT id, timestamp, response_time_ms, payload_bytes, is_up 
        FROM response_times 
        WHERE timestamp >= ? AND timestamp < ? AND exported = 0
        ORDER BY unix_timestamp ASC
    ''', (zeroed_start_timestamp, end_timestamp))
    
    return c.fetchall()


def mark_as_exported(c: sqlite3.Cursor, ids: list[int]) -> None:
    c.execute('UPDATE response_times SET exported = 1 WHERE id IN ({})'.format(','.join('?'*len(ids))), ids)
    conn.commit()


def generate_csv_report(week_data: list, end_date: str, destination_folder: str) -> None:
    filename = f'weekly_report_{end_date}.csv'
    reports_folder = "reports"
    os.makedirs(reports_folder, exist_ok=True)
    file_path = os.path.join(reports_folder, filename)
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['id', 'timestamp', 'response_time_ms', 'payload_bytes', 'is_up'])
        csvwriter.writerows(week_data)
    print(f'Report generated: {filename}')
    if destination_folder:
        copy_file_to_destination(file_path, destination_folder)


def generate_txt_report(start_date: str, end_date: str, week_data: list, destination_folder: str) -> None:
    total_uptime = sum(1 for row in week_data if row[4] == 1)
    total_downtime = len(week_data) - total_uptime

    filename = f'weekly_uptime_report_{end_date}.txt'
    reports_folder = "reports"
    os.makedirs(reports_folder, exist_ok=True)
    file_path = os.path.join(reports_folder, filename)
    with open(file_path, 'w') as txtfile:
        txtfile.write(f'Start Date: {start_date}\n')
        txtfile.write(f'End Date: {end_date}\n')
        txtfile.write(f'Total time of operation: {total_uptime} (Minutes / w)\n')
        txtfile.write(f'Total time of unavailability: {total_downtime} (Minutes / w)\n')
    print(f'Uptime report generated: {filename}')
    if destination_folder:
        copy_file_to_destination(file_path, destination_folder)


def create_weekly_reports(c: sqlite3.Cursor, destination_folder: str) -> None:
    first_unexported_timestamp = get_first_unexported_timestamp(c)
    if not first_unexported_timestamp:
        print("No unexported rows found.")
        return
    
    week_number = 1
    while True:
        weekly_data = fetch_weekly_data(c, first_unexported_timestamp)
        if not weekly_data:
            break
        
        start_date = datetime.strptime(first_unexported_timestamp, '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0, second=0)
        if (datetime.now() - start_date).days < 7:
            print(f"Week starting {start_date} does not span a full 7 days. Skipping.")
            break

        end_date = start_date + timedelta(days=6, hours=23, minutes=59)
        end_date_str = end_date.strftime('%Y-%m-%d')

        generate_csv_report(weekly_data, end_date_str, destination_folder)
        generate_txt_report(start_date.strftime('%Y-%m-%d'), end_date_str, weekly_data, destination_folder)
        
        ids = [row[0] for row in weekly_data]
        mark_as_exported(c, ids)
        
        first_unexported_timestamp = (start_date + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        week_number += 1
    

def copy_file_to_destination(file_path: str, destination_folder: str) -> None:
    source_file = Path(file_path)
    destination_file = Path(destination_folder) / source_file.name
    shutil.copy(str(source_file), str(destination_file))


if __name__ == "__main__":
    settings = load_settings('settings.json')
    destination_folder = settings.get('destination_folder')
    conn = sqlite3.connect('response_times.db')
    c = conn.cursor()
    create_weekly_reports(c, destination_folder)