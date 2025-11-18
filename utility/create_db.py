import sqlite3
import requests
import os
import time 

# Source URLs for Sakila database schema and datas
DB_FILE = "data/sakila.db"
SCHEMA_URL = "https://raw.githubusercontent.com/ivanceras/sakila/master/sqlite-sakila-db/sqlite-sakila-schema.sql"
# Note: In your original code, this URL pointed to a local file which might cause errors if setup runs. 
# I have reverted it to the web URL just in case you ever do need to re-download it.
DATA_URL = "https://raw.githubusercontent.com/ivanceras/sakila/master/sqlite-sakila-db/sqlite-sakila-insert-data.sql"

def setup_database():
    """
    Checks if database exists. If not, downloads and creates it.
    """
    
    # --- CHANGE 1: Check if file exists and SKIP if it does ---
    if os.path.exists(DB_FILE):
        print(f"Database '{DB_FILE}' already exists. Skipping download and setup.")
        return
    # ----------------------------------------------------------

    print(f"Creating new database: {DB_FILE}")
    
    try:
        # 2. Download the SQL files
        print(f"Downloading schema from {SCHEMA_URL}...")
        schema_sql = requests.get(SCHEMA_URL).text
        print("Schema download complete.")
        
        print(f"Downloading data from {DATA_URL}...")
        data_sql = requests.get(DATA_URL).text
        print("Data download complete.")

        # 3. Create database and load the SQL
        print("Connecting to database and executing SQL...")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            print("Creating tables (executing schema)...")
            cursor.executescript(schema_sql)
            print("Schema created.")
            
            print("Inserting data (executing data load)...")
            cursor.executescript(data_sql)
            print("Data inserted.")
            
        print("Database setup complete and connection closed.")

    except requests.RequestException as e:
        print(f"Error downloading SQL files: {e}")
    except sqlite3.Error as e:
        print(f"Error loading SQL into database: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def test_database():
    """
    Runs a simple query to verify the database was created correctly.
    """
    if not os.path.exists(DB_FILE):
        print(f"Database file '{DB_FILE}' not found. Run setup_database() first.")
        return

    print("\n--- Running Test Query ---")
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # We'll query the 'actor' table
            query = "SELECT first_name, last_name FROM actor LIMIT 5;"
            
            print(f"Executing: {query}")
            startTime = time.time()
            cursor.execute(query)
            endTine = time.time()
            print(f"Query executed in {endTine - startTime:.4f} seconds.")
            results = cursor.fetchall()
            
            if results:
                print("Test query successful. First results:")
                for i, row in enumerate(results):
                    print(f"  {i+1}: {row}")
            else:
                print("Test query ran but returned no results.")
                
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    setup_database()
    test_database()