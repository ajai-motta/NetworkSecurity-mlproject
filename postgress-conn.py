import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv
load_dotenv()

db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
def check_connection():
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,   # change if needed
            user=db_user,       # or your custom user (e.g., ajai)
            password=db_password,
            port=db_port,
            connect_timeout=5
        )

        # If connection succeeds
        print("✅ Connection to PostgreSQL successful!")

        # Optional: run a simple query
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        print("Test query result:", result)

        # Cleanup
        cur.close()
        conn.close()

    except OperationalError as e:
        print("❌ Connection failed!")
        print("Error:", e)


if __name__ == "__main__":
    check_connection()