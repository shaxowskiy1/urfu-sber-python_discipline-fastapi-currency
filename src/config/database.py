import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()


@contextmanager
def get_db_connection():

    connection = None
    try:
        # connection = psycopg2.connect(
        #     host=os.getenv('DB_HOST', 'localhost'),
        #     port=os.getenv('DB_PORT', '5432'),
        #     database=os.getenv('DB_NAME', 'db'),
        #     user=os.getenv('DB_USER', 'username'),
        #     password=os.getenv('DB_PASSWORD', 'password'),
        #
        #
        connection = psycopg2.connect(
            host='localhost',      
            port=5432,            
            database='db',        
            user='username',      
            password='password',  
            connect_timeout=5
        )
        try:
            yield connection
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            raise
    except psycopg2.Error as e:
        error_msg = str(e) if str(e) else f"Database connection error: {type(e).__name__}"
        raise RuntimeError(f"Ошибка подключения к базе данных: {error_msg}") from e
    except Exception as e:
        error_msg = str(e) if str(e) else f"Unexpected error: {type(e).__name__}"
        raise RuntimeError(f"Ошибка подключения к базе данных: {error_msg}") from e
    finally:
        if connection:
            connection.close()
