from sqlalchemy import create_engine, text

# Connect to the database
engine = create_engine('sqlite:///database.db')  # Replace with your DB file or connection string

# Drop a specific table
table_name = "your_table_name"  # Replace with the name of the table you want to drop
with engine.connect() as conn:
    conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
    print(f"Table '{table_name}' has been dropped.")
