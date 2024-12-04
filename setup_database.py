import pandas as pd
from sqlalchemy import create_engine


csv_file = "Dataset.csv"  
df = pd.read_csv(csv_file)

# Step 2: Create a SQLite Database
engine = create_engine('sqlite:///database.db')  # SQLite DB will be named 'database.db'

# Step 3: Write Data to the Database
table_name = "Country"  
df.to_sql(table_name, con=engine, if_exists="replace", index=False)

