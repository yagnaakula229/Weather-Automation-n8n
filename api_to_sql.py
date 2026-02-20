import requests
import sqlite3
import json
import requests
import sqlite3
import time
import json

# Database file name
DB_NAME = "workflow.db"

# Step 1: Create DB & table if it doesn't exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_data (
        id 
                   INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature TEXT,
        description TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# Step 2: Fetch weather data from API
def fetch_weather(city="Hyderabad"):
    url = f"https://wttr.in/{city}?format=j1"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        temp = data["current_condition"][0]["temp_C"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]
        return city, temp, desc
    except Exception as e:
        return None

# Step 3: Save fetched data into SQLite DB
def save_to_db(city, temp, desc):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO api_data (city, temperature, description) VALUES (?, ?, ?)", 
                   (city, temp, desc))
    conn.commit()
    conn.close()

# Step 4: Main workflow with retry logic
def run_workflow():
    init_db()
    retries = 2
    for attempt in range(retries):
        result = fetch_weather()
        if result:
            city, temp, desc = result
            save_to_db(city, temp, desc)
            return city, temp, desc
        else:
            time.sleep(2)
    return None

# Structured JSON output for n8n
if __name__ == "__main__":
    result = run_workflow()
    if result:
        city, temp, desc = result
        output = {
            "status": "success",
            "latest": {
                "city": city,
                "temperature": temp,
                "description": desc
            }
        }
        print(json.dumps(output))  # n8n reads this JSON
    else:
        print(json.dumps({"status": "failed"}))