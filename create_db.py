import sqlite3
import requests
import os

DB_FILE = "sakila.db"
SCHEMA_URL = "https://raw.githubusercontent.com/ivanceras/sakila/master/sqlite-sakila-db/sqlite-sakila-schema.sql"
DATA_URL = "https://raw.githubusercontent.com/ivanceras/sakila/master/sqlite-sakila-db/sqlite-sakila-insert-data.sql"

def setup_database():
    """
    Downloads Sakila schema and data, then loads them into an SQLite database.
    """
    
    # 1. Delete the old database file if it exists
    if os.path.exists(DB_FILE):
        print(f"Removing old database file: {DB_FILE}")
        os.remove(DB_FILE)

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
        # A connection will automatically create the file
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            
            # executescript can handle multiple SQL statements at once
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
            cursor.execute(query)
            
            results = cursor.fetchall()
            
            if results:
                print("Test query successful. First 5 actors:")
                for i, row in enumerate(results):
                    print(f"  {i+1}: {row[0]} {row[1]}")
            else:
                print("Test query ran but returned no results. Check data insertion.")
                
    except sqlite3.Error as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    # This will run when you execute the script
    setup_database()
    test_database()