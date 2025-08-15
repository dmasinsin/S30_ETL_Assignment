import sqlite3

# Connect (file is created if it doesn't exist)
conn = sqlite3.connect("../../sales.db")
cur = conn.cursor()

# Enforce foreign keys in SQLite
cur.execute("PRAGMA foreign_keys = ON;")

# NOTE: Kung gusto mong mag-reset ng maling lumang tables,
# i-uncomment mo 'to bago ang CREATEs:
# cur.executescript("""
# DROP TABLE IF EXISTS Orders;
# DROP TABLE IF EXISTS Sales;
# DROP TABLE IF EXISTS Items;
# DROP TABLE IF EXISTS Customer;
# """)

cur.executescript("""
-- Customer(customer_id, age)
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    age INTEGER NOT NULL
);

-- Items(item_id, item_name)
CREATE TABLE IF NOT EXISTS items (
    item_id   INTEGER PRIMARY KEY,
    item_name TEXT NOT NULL
);

-- Sales(sales_id, customer_id) -> Customer
CREATE TABLE IF NOT EXISTS sales (
    sales_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Orders(order_id, sales_id, item_id, quantity) -> Sales, Items
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    sales_id INTEGER NOT NULL,
    item_id  INTEGER NOT NULL,
    quantity INTEGER,
    FOREIGN KEY (sales_id) REFERENCES sales(sales_id),
    FOREIGN KEY (item_id)  REFERENCES items(item_id)
);

-- Optional but helpful indexes on FKs
CREATE INDEX IF NOT EXISTS idx_sales_customer_id ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_sales_id   ON orders(sales_id);
CREATE INDEX IF NOT EXISTS idx_orders_item_id    ON orders(item_id);
""")

conn.commit()
conn.close()
