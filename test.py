import mysql.connector
from utils.email_sender import send_otp

print(send_otp("your_email@gmail.com", "123456"))

print("Step 1")

connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="gomon_db",
    port=3306
)

print("Step 2")
connection.close()
print("Finished")