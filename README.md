# Response measurer

This is a small python app that measures given SQL database's response time and payload size. Use any modern python version to run the project's main scripts app.py and export.py. Tested to run at least with python 3.11 and 3.12. The app uses SQLite to store measurements in response_times.db database.

## How it works

The main measuring script makes simple database queries to target database every minute. These end to end queries are timed to find out the complete response time of the database server measured in milliseconds. The size of the query payload is measured in bytes. Each measurement is stored into local SQLite db. For each measurement timestamps, response time, payload size and "is up" status (is the measurement target up or down) is stored.´

The export script handles exporting weekly reports. The script works by getting all unexported full 7 day week periods worth of measuring data and creating two report files of each full unexported week. The first report type is a raw row data csv file and the second type is a total uptime summary txt file. The reports are created under "reports" folder. Additionally copies of these reports are made to desired folder location when this folder location is given in the settings file.

A test export can be made with script test_export.py. This will create a file "test_report.csv" with a single data row.

## Installing

To use the app first init and activate venv e.g. in Windows:
```
python -m venv venv
venv\Scripts\activate
```

Install requirements:
```
pip install -r requirements.txt
```

Create file `settings.json` based on `example_settings.json`. Each setting explained:
- `server` the address for your target database's server.
- `database`: the database name you are targeting.
- `table`: the database table you are targeting for measurements.
- `driver`: `pyodbc` uses this to connect to the SQL db. Use `"{SQL Server}"` unless you have some specific needs for other drivers.
- `destination_folder`: the folder `export.py` makes additional copies of exported report files into. Leave empty `""` if you don't want additional copies. Note that folder path needs to use "/" format i.e. this/is/my/path.
- `network_test_addr`: URL to check whether network is working or not when making measurements. Leave empty `""` if you don't want this additional network test.

## Running the app

Start running measuring every minute:
```
python app.py
```

When you want to export measurements into auto created "reports" folder, run:
```
python export.py
```