import json
import os
import time

import psycopg2
from read_pump import TwisTorr

# Pump connection parameters
PUMP_ADDRESS = os.getenv("PUMP_ADDRESS", "localhost")
PUMP_PORT = int(os.getenv("PUMP_PORT", "8899"))
LOOP_INTERVAL = 5  # seconds

# PostgreSQL connection parameters
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "localhost")
POSTGRESQL_PORT = int(os.getenv("POSTGRESQL_PORT", "5432"))
POSTGRESQL_DATABASE = os.getenv("POSTGRESQL_DATABASE", "grafana")
POSTGRESQL_TABLE = os.getenv("POSTGRESQL_TABLE", "twistorr_data_1")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")  # Replace with your actual password

pump, db = None, None  # Initialize pump and database connection as None

def connect():
    pump = TwisTorr()
    print("Connecting to pump...")
    pump.open(PUMP_ADDRESS, PUMP_PORT)
    print("Connected to pump.")
    db = psycopg2.connect(
        host=POSTGRESQL_HOST,
        port=POSTGRESQL_PORT,
        database=POSTGRESQL_DATABASE,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    if db is None:
        print("Failed to connect to PostgreSQL database.")
        raise ConnectionError("Could not connect to PostgreSQL database.")
    print("Connected to PostgreSQL database.")
    # Create table if it does not exist
    with db.cursor() as cur:
        cur.execute(f"CREATE TABLE IF NOT EXISTS {POSTGRESQL_TABLE} (time TIMESTAMP UNIQUE, data JSONB);")
    db.commit()
    return pump, db


def convert_to_snake_case(data):
    """Convert camelCase keys in data dictionary to snake_case."""
    return {key.replace(" ", "_").lower(): value for key, value in data.items()}


while True:
    timestamp = time.time_ns()
    data = {}
    try:
        if not pump or not db: # Reconnect if connection is lost
            pump, db = connect()
        data["PRESSURE READING"] = float(pump.read("PRESSURE READING")[3])
        if data["PRESSURE READING"] <= 0:
            print("Pressure reading is zero or negative, skipping data read.")
            time.sleep(LOOP_INTERVAL)
            continue
        for param in [
            "PUMP TEMPERATURE",
            # "UNIT OF MEASURE FOR PRESSURE",
            "CYCLE NUMBER",
            "PUMP POWER",
            "PUMP STATUS",
            "ERROR CODE",
            "PUMP LIFE IN HOURS",
            "CYCLE TIME IN MINUTES",
            "ROTATION FREQUENCY",
        ]:
            print(f"Reading {param}...")
            data[param] = int(pump.read(param)[3])
        data["PRESSURE READING"] = float(pump.read("PRESSURE READING")[3])
        data["TURBO_PUMP_ON"] = bool(int(pump.read("START/STOP")[3]))
        data = convert_to_snake_case(data)
        print(timestamp / 1e9, data)
        # Insert data into PostgreSQL table
        pg_query = f"insert into {POSTGRESQL_TABLE} (time, data) values (NOW(), '{json.dumps(data)}') ON CONFLICT (time) DO UPDATE SET data = {POSTGRESQL_TABLE}.data || EXCLUDED.data;"
        with db.cursor() as cur:
            cur.execute(pg_query)
        db.commit()
        time.sleep(time.time() - timestamp / 1e9 + LOOP_INTERVAL)  # Adjust sleep to maintain loop timing

    except Exception as e:
        print(f"Error reading data: {e}")
        time.sleep(LOOP_INTERVAL * 3)
        pump, db = None, None  # Force reconnect on error
        continue
    except KeyboardInterrupt:
        print("Exiting...")
        break
