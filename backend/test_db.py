import mysql.connector
from config import DB_CONFIG

try:
    connection = mysql.connector.connect(**DB_CONFIG)

    if connection.is_connected():
        print("RescueMeal database connected successfully!")

    connection.close()

except mysql.connector.Error as error:
    print("Database connection failed:", error)