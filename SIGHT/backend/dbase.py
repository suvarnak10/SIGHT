import os
import psycopg2
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get the connection string from the environment variable
connection_string = 'postgresql://cgaswin:4fE2RHFeQnpC@ep-cold-morning-42359364.us-east-2.aws.neon.tech/cryptcode?sslmode=require'

# Connect to the Postgres database
conn = psycopg2.connect(connection_string)

# Create a cursor object
cur = conn.cursor()
'''
# Execute SQL commands to retrieve the current time and version from PostgreSQL
cur.execute('SELECT NOW();')
time = cur.fetchone()[0]

cur.execute('SELECT version();')
version = cur.fetchone()[0]
'''

cur.execute('SELECT * FROM Users;')
tables = cur.fetchall()

cur.execute("INSERT INTO Users (email, name, password) VALUES (%s, %s, %s)", ('suvarna@gmail.com', 'Suvarna', '1234'))
cur.execute("INSERT INTO Users (email, name, password) VALUES (%s, %s, %s)", ('duyoof@gmail.com', 'Duyoof', '5678'))

# Close the cursor and connection
conn.commit()

cur.execute('SELECT * FROM Users;')
tables = cur.fetchall()

cur.close()
conn.close()

# Print the results
#print('Current time:', time)
#print('PostgreSQL version:', version)
print('PostgreSQL table:', tables)
