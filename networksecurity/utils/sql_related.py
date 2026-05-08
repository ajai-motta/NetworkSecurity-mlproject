import psycopg2
from psycopg2 import OperationalError
from networksecurity.exception.exception import CustomException
import sys
import os
from dotenv import load_dotenv
load_dotenv()

def connect_to_postgres():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        print("Connected to PostgreSQL successfully!")

        return connection

    except OperationalError as e:
        raise CustomException(e,sys)

        