import pytest 
from habits import Habits
from datetime import datetime, timedelta
from unittest.mock import patch
import sqlite3

class TestHabits:

    # scoped to the session so it runs once before all tests
    @pytest.fixture(scope="session")
    def db_connection(self):
        """ fixture to create the database connection and the cursor """

        conn = sqlite3.connect("test.db") # connect to the database
        cur = conn.cursor() # create the cursor

        # create the habit and reset_log tables
        cur.executescript(
           """ CREATE TABLE IF NOT EXISTS habit(
           name TEXT PRIMARY KEY,
           periodicity INTEGER,
           streak INTEGER,
           longest_streak INTEGER,
           checked_off INTEGER,
           creation_time TEXT,
           milestone INTEGER
           );

           CREATE TABLE IF NOT EXISTS reset_log(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           habit_name TEXT,
           missed_time TEXT,
           FOREIGN KEY (habit_name) REFERENCES habit (name)
           ); """
       )
        conn.commit()

        yield conn,cur  # return connection and cursor
      
        conn.close()    # close connection after test

    @pytest.fixture
    def test_habit1(self):
        """ fixture for a habit object """
        test_habit1 = Habits(name = "gym", periodicity = "1", streak = 9, milestone = 1, missed_time = 3, longest_streak = 14, creation_time = datetime.now(), checked_off = 0, db_name="test.db")
        return test_habit1
    
    @pytest.fixture
    def clear_db(self, db_connection):
        """ fixture that clears the database before every new entry """
        # unpack connection and cursor 
        conn, cur = db_connection 
        #remove the tables from the database
        cur.execute("DELETE FROM habit;")
        cur.execute("DELETE FROM reset_log;")
        # save the changes 
        conn.commit()

    def test_check_off(self, test_habit1):
        """ testing if check_off increases streak & longest_streak when the habit isn't checked off already, that the user gets an information that the habit is already checked off and that longest_streak is getting updated """

        # testing when the habit is not checked off yet (checked_off = 0)
        result = test_habit1.check_off()

        # assert the streak is increased by 1
        assert test_habit1.streak == 10

        # assert the checked_off attribute is now set to 1
        assert test_habit1.checked_off == 1

        # assert the returned message is as expected
        result == "You checked off the habit 'gym'.\n Awesome! You are on a 10 day streak - keep going ! \n"

        # assert that the longest_streak has not been incremented
        assert test_habit1.longest_streak == 14


        # test when the habit is already checked off (checked_off == 1)
        result = test_habit1.check_off()

        # assert that the streak is not changed
        assert test_habit1.streak == 10

        # assert that the checked_off attribute is still 1
        assert test_habit1.checked_off == 1

        # assert that the returned message is as expected
        result == "You already checked off your habit - good job! Now let's work on your other habits :)"


        # test when the streak is greater than the largest streak
        test_habit1.streak = 14
        # reset the checked_off so streak gets incremented when check_off is called again
        test_habit1.checked_off = 0

        result = test_habit1.check_off()

        # assert that the longest_streak is updated
        assert test_habit1.longest_streak == 15

    def test_increment_milestone(self, test_habit1):
        """ testing if increment_milestone correctly increments the milestone value only when the streak is a multiple of 7 """

        test_habit1.streak = 7
        test_habit1.milestone = 0
        result = test_habit1.increment_milestone()

        # assert that the milestone is incremented to 1
        assert test_habit1.milestone == 1

        # assert that the returned string is correct
        assert result == f"YAAAY - you've managed to hit a milestone! You checked off {test_habit1.name} 7 times in a row, you can be proud of your dedication! Keep going and get the next milestone!\n"

        # test when the streak is not a multiple of 7
        test_habit1.streak = 5
        test_habit1.milestone = 0
        result = test_habit1.increment_milestone()

        # assert that the milestone has not changed
        assert test_habit1.milestone == 0

        # assert that the returned string is empty (no message)
        assert result == ""
        
    def test_reset_checked_off(self, test_habit1, clear_db, db_connection):

        """  test if reset_checked_off() correctly resets streak and checked off """

        # unpack the tuple of connection and cursor
        conn, cur =  db_connection

        # insert the habit data into the database
        cur.execute(
            """ INSERT OR REPLACE INTO habit (
            name,
            periodicity,
            streak,
            longest_streak,
            checked_off,
            creation_time,
            milestone) VALUES (?,?,?,?,?,?,?)""",
            (test_habit1.name, test_habit1.periodicity, test_habit1.streak, test_habit1.longest_streak,
         test_habit1.checked_off, test_habit1.creation_time.strftime('%Y-%m-%d %H:%M:%S'), test_habit1.milestone)
        )
        # save the changes
        conn.commit()

        # adjust the creation_time to 1 day in the past so creation_time + periodicity equals datetime.now()
        test_habit1.creation_time = (datetime.now() - timedelta(days=int(test_habit1.periodicity)))

        # call reset_checked_off()
        test_habit1.reset_checked_off()

        # fetch updated habit data from the database
        cur.execute("SELECT streak, checked_off, creation_time, milestone FROM habit WHERE name = ?", (test_habit1.name,))
        # store the fetched values from fetchone (which fetches one row from the SQL query) in new variables
        updated_streak, updated_checked_off, updated_creation_time, updated_milestone = cur.fetchone()

        # convert the creation_time back to a datetime object
        updated_creation_time = datetime.strptime(updated_creation_time,"%Y-%m-%d %H:%M:%S")

        # expected next period start
        expected_creation_time = (test_habit1.creation_time + timedelta(days=int(test_habit1.periodicity)))

        # test when the habit was not checked off 
        if test_habit1.checked_off == 0:
            assert updated_streak == 0
            assert updated_milestone == 0

            # check if the reset_log table was updated with the missed time
            cur.execute("SELECT COUNT (*) FROM reset_log WHERE name = ?", (test_habit1.name,))
            reset_log_count = cur.fetchone()[0]
            assert reset_log_count == 1

        # check if the check_off value was reset to 0
        assert updated_checked_off == 0

        # check if the creation time was updated correctly
        assert updated_creation_time.date() == expected_creation_time.date()

  


