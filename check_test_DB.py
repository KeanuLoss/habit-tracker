import sqlite3

db_name = "test.db"  # Use the name of your database file

with sqlite3.connect(db_name) as db:
    cur = db.cursor()

    # fetch column names 
    cur.execute("PRAGMA table_info(habit)")
    columns = [col[1] for col in cur.fetchall()]

    # fetch all rows
    cur.execute("SELECT * FROM habit")  # Fetch all rows from the habit table
    rows = cur.fetchall()  # Get all rows
    
    if rows:
        print("Database Contents:")
        print(" | ".join(columns))
        print("-" * 50) # seperator line
        for row in rows:
            print(" | ".join(str(value) for value in row))
    else:
        print("The habit table is empty.")

    # fetch column names 
    cur.execute("PRAGMA table_info(reset_log)")
    columns = [col[1] for col in cur.fetchall()]

    cur.execute("SELECT * from reset_log") # fetch all rows from the reset_log table
    missed_time_rows = cur.fetchall()

    if missed_time_rows:
        print("Database Contents:")
        print(" | ".join(columns))
        print("-" * 50) # seperator line
        for row in missed_time_rows:
            print(" | ".join(str(value) for value in row))
    else:
        print("The reset_log table is empty.")
