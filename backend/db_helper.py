from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()
# Conexão MySQL
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

def get_order_status(order_id):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM order_tracking WHERE order_id = %s", (order_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None