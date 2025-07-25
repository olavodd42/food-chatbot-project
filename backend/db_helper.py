from dotenv import load_dotenv
from typing import Dict
import mysql.connector
import os

load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "<PASSWORD>"),
    "database": os.getenv("DB_NAME", "db"),
}

def get_order_status(order_id: int) -> str:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM order_tracking WHERE order_id = %s", (order_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def save_to_db(order: Dict[str, int], session_id: str) -> int:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1) Cria o header do pedido
    cursor.execute(
        "INSERT INTO order_header (session_id) VALUES (%s)",
        (session_id,)
    )
    header_id = cursor.lastrowid
    print(f"[DEBUG] INSERT header -> order_header.id = {header_id}")

    # 2) Insere cada item
    insert_item_sql = """
                      INSERT INTO orders (header_id, food_id, quantity, total_price)
                      VALUES (%s, %s, %s, %s) \
                      """
    for food_name, qty in order.items():
        cursor.execute(
            "SELECT id, price FROM food_items WHERE LOWER(name) LIKE %s LIMIT 1",
            (f"%{food_name.lower()}%",)
        )
        row = cursor.fetchone()
        if not row:
            print(f"[WARN] Item não encontrado no catálogo: '{food_name}'")
            continue
        food_id, unit_price = row
        total_price = float(unit_price) * qty
        cursor.execute(insert_item_sql, (header_id, food_id, qty, total_price))
        print(f"[DEBUG] INSERT orders -> (header_id={header_id}, food_id={food_id}, qty={qty}, total={total_price})")

    conn.commit()
    print("[DEBUG] Committed orders")

    # 3) Inicializa tracking
    cursor.execute(
        "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)",
        (header_id, "Pending")
    )
    conn.commit()
    print(f"[DEBUG] INSERT order_tracking -> order_id = {header_id}")

    cursor.close()
    conn.close()

    return header_id

