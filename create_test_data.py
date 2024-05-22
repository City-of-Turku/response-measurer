import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('response_times.db')
c = conn.cursor()

c.execute('''
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


def generate_test_data(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        timestamp = current_date.strftime('%Y-%m-%d %H:%M:%S')
        unix_timestamp = int(current_date.timestamp())
        response_time_ms = round(random.uniform(50, 3000), 2)
        payload_bytes = random.randint(100, 10000)
        is_up = random.choice([True, False])
        exported = False
        
        yield (timestamp, unix_timestamp, response_time_ms, payload_bytes, is_up, exported)
        
        current_date += timedelta(minutes=1)

start_date = datetime.now() - timedelta(weeks=2)
end_date = datetime.now() + timedelta(weeks=1)

test_data = generate_test_data(start_date, end_date)

c.executemany('''
INSERT INTO response_times (timestamp, unix_timestamp, response_time_ms, payload_bytes, is_up, exported)
VALUES (?, ?, ?, ?, ?, ?)
''', test_data)

conn.commit()
conn.close()
