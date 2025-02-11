import sqlite3

db_name = "habit.db"  # Use the name of your database file

with sqlite3.connect(db_name) as db:
    cur = db.cursor()
    cur.execute("SELECT * FROM habit")  # Fetch all rows from the habit table
    rows = cur.fetchall()  # Get all rows
    
    if rows:
        print("Database Contents:")
        for row in rows:
            print(row)
    else:
        print("The habit table is empty.")

    cur.execute("SELECT * from reset_log") # fetch all rows from the reset_log table
    missed_time_rows = cur.fetchall()

    if missed_time_rows:
        print("Database Content:")
        for row in missed_time_rows:
            print(row)
    else:
        print("The reset_log table is empty.")

