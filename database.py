import mysql.connector
from mysql.connector import Error
import bcrypt

def connect_db():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="gomon_db",
            port=3306,
            use_pure=True
        )
        return connection
    except Error as e:
        print("DB Error:", e)
        return None


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())