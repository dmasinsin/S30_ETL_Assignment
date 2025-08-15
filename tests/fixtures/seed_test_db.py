# tests/fixtures/seed_test_db.py
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("test_sales.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Sales;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Customer;

CREATE TABLE Customer (
  customer_id INTEGER PRIMARY KEY,
  age         INTEGER NOT NULL
);

CREATE TABLE Items (
  item_id   INTEGER PRIMARY KEY,
  item_name TEXT NOT NULL
);

CREATE TABLE Sales (
  sales_id    INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

CREATE TABLE Orders (
  order_id INTEGER PRIMARY KEY,
  sales_id INTEGER NOT NULL,
  item_id  INTEGER NOT NULL,
  quantity INTEGER,
  FOREIGN KEY (sales_id) REFERENCES Sales(sales_id),
  FOREIGN KEY (item_id)  REFERENCES Items(item_id)
);
"""

def main():
    if DB.exists():
        DB.unlink()

    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.executescript(SCHEMA)

        # Items catalog: x, y, z
        cur.executemany(
            "INSERT INTO Items(item_id, item_name) VALUES(?, ?)",
            [(1, "x"), (2, "y"), (3, "z")],
        )

        # Customers: three within range 18-35, one out-of-range as a guardrail
        cur.executemany(
            "INSERT INTO Customer(customer_id, age) VALUES(?, ?)",
            [(1, 21), (2, 23), (3, 35), (4, 42)],
        )

        # Sales headers: two for customer 1, one for customer 2, one for customer 3, one for customer 4
        cur.executemany(
            "INSERT INTO Sales(sales_id, customer_id) VALUES(?, ?)",
            [(1, 1), (2, 1), (3, 2), (4, 3), (5, 4)],
        )

        # Orders lines
        # Customer 1: item x totals to 10 (6 + 4). Also a NULL for item y to validate COALESCE.
        cur.executemany(
            "INSERT INTO Orders(order_id, sales_id, item_id, quantity) VALUES(?, ?, ?, ?)",
            [
                (1, 1, 1, 6),     # sale 1, item x, qty 6
                (2, 2, 1, 4),     # sale 2, item x, qty 4  -> total 10
                (3, 1, 2, None),  # sale 1, item y, qty NULL -> should not appear
            ],
        )

        # Customer 2: one each of x, y, z
        cur.executemany(
            "INSERT INTO Orders(order_id, sales_id, item_id, quantity) VALUES(?, ?, ?, ?)",
            [
                (4, 3, 1, 1),
                (5, 3, 2, 1),
                (6, 3, 3, 1),
            ],
        )

        # Customer 3: two of z, plus a NULL on y for COALESCE validation
        cur.executemany(
            "INSERT INTO Orders(order_id, sales_id, item_id, quantity) VALUES(?, ?, ?, ?)",
            [
                (7, 4, 3, 2),     # item z, qty 2
                (8, 4, 2, None),  # item y, NULL -> should not appear
            ],
        )

        # Customer 4: out-of-range age. Should not show in results.
        cur.executemany(
            "INSERT INTO Orders(order_id, sales_id, item_id, quantity) VALUES(?, ?, ?, ?)",
            [
                (9, 5, 1, 999),
            ],
        )

        conn.commit()

    print(f"Created fixture DB at {DB.resolve()}")

if __name__ == "__main__":
    main()
