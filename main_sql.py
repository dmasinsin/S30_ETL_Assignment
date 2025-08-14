# main_sql.py
import argparse
import csv
import os
import sqlite3
from pathlib import Path

SQL = """SELECT
  c.customer_id AS Customer,
  c.age         AS Age,
  i.item_name   AS Item,
  CAST(SUM(COALESCE(o.quantity, 0)) AS INTEGER) AS Quantity
FROM Customer c
JOIN Sales   s ON s.customer_id = c.customer_id
JOIN Orders  o ON o.sales_id    = s.sales_id
JOIN Items   i ON i.item_id     = o.item_id
WHERE c.age BETWEEN 18 AND 35
GROUP BY c.customer_id, c.age, i.item_name
HAVING SUM(COALESCE(o.quantity, 0)) > 0
ORDER BY Customer, Item;
"""

def parse_args():
    p = argparse.ArgumentParser(description="ETL - SQL engine")
    p.add_argument("--db", default="./sales.db", help="Path to SQLite database")
    p.add_argument("--out", default="./output", help="Output directory")
    return p.parse_args()

def main():
    args = parse_args()
    db_path = Path(args.db)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "sales_by_item_18_35_sql.csv"

    with sqlite3.connect(db_path) as conn, open(out_file, "w", newline="") as f:
        cur = conn.execute(SQL)
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Customer", "Age", "Item", "Quantity"])
        for row in cur.fetchall():
            writer.writerow(row)

    print(f"[SQL] Wrote file: {out_file.resolve()}")

if __name__ == "__main__":
    main()
