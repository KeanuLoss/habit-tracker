import pytest 

from datetime import datetime, timedelta, time
from habit_manager import HabitManager
from habits import Habits
import sqlite3
from unittest.mock import patch

# test all the different methods from the HabitManager class 
# best practice : use test_ prefix to all functions 
# you need to call the function you want to test by using the file-name.function-name and passing arguments as needed 


class TestHabitManager:
    """ This class will be used to test the methods of the class HabitManager """

    # scoped to the session so it runs once before all tests
    @pytest.fixture(scope="session")
    def db_connection(self):
        """ fixture to create the database connection and the cursor """
        conn = sqlite3.connect("test.db") # connect to the database
        cur = conn.cursor() # create the cursor

        # create an instance of HabitManager and initialize the database
        hm = HabitManager()
        hm.db_name = "test.db"
        hm.initialize_database()

        yield conn,cur  # return connection and cursor
      
        conn.close()    # close connection after test

    @pytest.fixture
    def hm(self):
        """ fixture that creates an instance of HabitManager to call methods from HabitManager """
        # pass test.db into the HabitManager for creating the database
        return HabitManager(db_name="test.db")

    @pytest.fixture
    def test_habit1(self):
        """ fixture that creates an instance of Habits to call methods from habits """
        test_habit1 = Habits(name = "gym", periodicity = "1", streak = 9, milestone = 1, missed_time = 3, longest_streak = 14, creation_time = datetime.now(), checked_off = 0, db_name="test.db")
        return test_habit1
    
    @pytest.fixture
    def test_habit2(self):
        """ fixture that creates an instance of Habits to call methods from habits """
        test_habit2 = Habits(name = "cardio", periodicity = "3", streak = 7, milestone = 1, missed_time = 3, longest_streak = 7, creation_time = datetime.now(), checked_off = 1, db_name= "test.db")
        return test_habit2
    
    @pytest.fixture
    def test_habit3(self):
        """ fixture that creates an instance of Habits to call methods from habits """
        test_habit2 = Habits(name = "visit grandma", periodicity = "7", streak = 4, milestone = 0, missed_time = 0, longest_streak = 4, creation_time = datetime.now(), checked_off = 0, db_name = "test.db")
        return test_habit2
    
    @pytest.fixture
    def test_habit4(self):
        """ fixture that creates an instance of Habits to call methods from habits """
        test_habit2 = Habits(name = "drink 2l water", periodicity = "1", streak = 28, milestone = 4, missed_time = None, longest_streak = 28, creation_time = datetime.now(), checked_off = 1, db_name = "test.db")
        return test_habit2
    
    @pytest.fixture
    def test_habit5(self):
        """ fixture that creates an instance of Habits to call methods from habits """
        test_habit2 = Habits(name = "clean windows", periodicity = "28", streak = 1, milestone = 0, missed_time = None, longest_streak = 1, creation_time = datetime.now(), checked_off = 0, db_name = "test.db")
        return test_habit2
    
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
        
    def test_initialize_database(self,hm, clear_db):
        """ testing if initialize_database creates tables correctly """
        # clear_db is automatically run before the test function starts because pytest automatically injects it

        # create a database connection & cursor
        conn = sqlite3.connect("test.db")
        cur = conn.cursor()

        # call the function initialize_database
        hm.db_name = "test.db"
        hm.initialize_database()

        #check if tables exist
        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' and name = 'habit'
            """)
        habit_table = cur.fetchone()

        cur.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'reset_log'
            """)
        reset_log_table = cur.fetchone()

        # close connection after test 
        conn.close()

        assert habit_table is not None
        assert reset_log_table is not None

    def test_load_habits_into_memory(self, db_connection, hm):
        """ testing if the data from the database is stored in the in-memory storage  """
        # unpack the tuple of connection and cursor 
        conn, cur = db_connection 

        # insert test data using cursor
        cur.execute(
            """
            INSERT INTO habit (name, periodicity, streak, longest_streak, checked_off, creation_time, milestone)
            VALUES (?,?,?,?,?,?,?)
        """, ("Yoga", 2, 2, 5, True, "2025-01-31", 0))

        conn.commit() # commit changes

        # load habits into memory 
        hm.db_name = "test.db"
        hm.load_habits_into_memory()

        # assert : verify that habit was loaded into memory 
        assert "Yoga" in hm.habits 
        yoga = hm.habits["Yoga"]
        assert yoga.name == "Yoga"
        assert yoga.streak == 2

    def test_habit_exists(self, hm, test_habit1, test_habit2):
        """ testing if habit_exists correctly identifies existing habits in the in-memory storage  """
        
        # add habits into the in-memory storage self.habits
        hm.habits[test_habit1.name] = test_habit1
        hm.habits[test_habit2.name] = test_habit2

        # test if habit_exists returns True for an existing habit
        assert hm.habit_exists(test_habit1.name) is True
        assert hm.habit_exists(test_habit2.name) is True

        # test if habit_exists returns False for a non-existing habit 
        assert hm.habit_exists("NonExistentHabit") is False 

    def test_add_habit(self, db_connection, hm, test_habit1):
        """ testing if habits get correctly added to the memory and database """

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name 
        hm.db_name = "test.db"

        # add a habit
        hm.add_habit(test_habit1.name, test_habit1.periodicity)

        # assert that the habit is added to the in-memory storage
        # normalize habit name to lowercase
        assert test_habit1.name.lower() in hm.habits 
        habit = hm.habits[test_habit1.name.lower()]
        assert habit.name == test_habit1.name
        assert habit.periodicity == int(test_habit1.periodicity)

        # assert that the habit is added to the database
       

        cur.execute("SELECT * FROM habit WHERE name = ?", (test_habit1.name.lower(),))
        habit_row = cur.fetchone()
        assert habit_row is not None
        assert habit_row[0] == test_habit1.name.lower()
        assert habit_row[1] == int(test_habit1.periodicity)

        # check if a ValueError is raised when the same habit name is entered
        try: 
            hm.add_habit(test_habit1.name, test_habit1.periodicity)
        except ValueError as e:
            assert str(e) == f"You already have a habit with the name '{test_habit1.name}'. \nPlease choose another name for the habit you want to add.\n" 
    
    def test_delete_habit(self, db_connection, hm, test_habit1, clear_db ):
        """ testing if the habit gets deleted from the in-memory storage and database """

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name for HabitManager
        hm.db_name = "test.db"

        # add the habit to the in-memory storage and database 
        hm.add_habit(test_habit1.name, test_habit1.periodicity)

        # assert that the habit exists
        assert test_habit1.name.lower() in hm.habits

        # delete the habit
        hm.delete_habit(test_habit1.name)

        # assert that the habit is removed from the database
        cur.execute(" SELECT * FROM habit WHERE name = ?", (test_habit1.name.lower(),))
        # fetchone retrieves a single row from the result of a query
        habit_row = cur.fetchone()
        # ensure the habit is deleted from the database
        assert habit_row is None 


        # assert that the habit is also deleted from the reset_log table
        cur.execute("SELECT * FROM reset_log WHERE name = ?", (test_habit1.name.lower(),))
        reset_log_row = cur.fetchone()
        
        # ensure the habit is deleted from the reset_log table
        assert reset_log_row is None
        
    def test_check_off_habit(self, db_connection, hm, test_habit1, clear_db):

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

        # add a habit to the memory and database
        hm.add_habit(test_habit1.name, test_habit1.periodicity)

        # ensure the habit is in the in-memory storage
        assert test_habit1.name.lower() in hm.habits

        # check the initial values
        habit = hm.habits[test_habit1.name.lower()]
        assert habit.streak == 0
        initial_streak = habit.streak
        assert habit.longest_streak == 0
        assert habit.checked_off == 0

        # check off the habit
        hm.check_off_habit(test_habit1.name.lower())

        # reload the habit data from the database
        cur.execute("SELECT streak, longest_streak, checked_off FROM habit WHERE name = ?", (test_habit1.name.lower(),))
        db_streak, db_longest_streak, db_checked_off = cur.fetchone()

        assert habit.checked_off == 1
        assert habit.streak == initial_streak +1
        assert habit.longest_streak >= habit.streak 
        assert db_streak == habit.streak
        assert db_longest_streak == habit.longest_streak
        assert db_checked_off == 1

    def test_get_all_habits(self, hm, test_habit1, test_habit2, test_habit3, test_habit4, test_habit5):

        # add habits to the in-memory storage
        hm.habits[test_habit1.name.lower()] = test_habit1
        hm.habits[test_habit2.name.lower()] = test_habit2 
        hm.habits[test_habit3.name.lower()] = test_habit3 
        hm.habits[test_habit4.name.lower()] = test_habit4 
        hm.habits[test_habit5.name.lower()] = test_habit5 

        # fetch all habits
        all_habits = hm.get_all_habits()

        # check if the returned dictionary contains the added habit data
        assert test_habit1.name.lower() in all_habits
        assert test_habit2.name.lower() in all_habits
        assert test_habit3.name.lower() in all_habits
        assert test_habit4.name.lower() in all_habits
        assert test_habit5.name.lower() in all_habits

        # validate habit attributes and that the function accurately reflects what's in memory
        # extract the periodicity values from the test habit object
        # the first bracket retrieves the inner dictionary and the second bracket extracts the periodicity / streak value
        assert all_habits[test_habit1.name.lower()]["periodicity"] == test_habit1.periodicity
        assert all_habits[test_habit2.name.lower()]["periodicity"] == test_habit2.periodicity
        assert all_habits[test_habit3.name.lower()]["periodicity"] == test_habit3.periodicity
        assert all_habits[test_habit4.name.lower()]["periodicity"] == test_habit4.periodicity
        assert all_habits[test_habit5.name.lower()]["periodicity"] == test_habit5.periodicity

        assert all_habits[test_habit1.name.lower()]["streak"] == test_habit1.streak
        assert all_habits[test_habit2.name.lower()]["streak"] == test_habit2.streak
        assert all_habits[test_habit3.name.lower()]["streak"] == test_habit3.streak
        assert all_habits[test_habit4.name.lower()]["streak"] == test_habit4.streak
        assert all_habits[test_habit5.name.lower()]["streak"] == test_habit5.streak

    # pytest.mark.parametrize allows testing multiple cases with different periodicitees
    @pytest.mark.parametrize("periodicity, expected", [
        (1, "daily"),
        (7, "weekly"),
        (28, "monthly"),
        (3, "every-3-day")
    ])

    def test_periodicity_to_text(self, hm, periodicity, expected):
        """ testing if periodicity_to_text returns the correct text representation """
        assert hm.periodicity_to_text(periodicity) == expected

    @pytest.mark.parametrize("periodicity, expected_message", [
        (1,"\nThese are your daily habits: \n\nhabit: gym, streak: 9\nhabit: drink 2l water, streak: 28"),
        # test if client wants to add functions of showing habits more detailed
        (3,"\nThese are your every-3-day habits: \n\nhabit: cardio, streak: 7"),
        (7,"\nThese are your weekly habits: \n\nhabit: visit grandma, streak: 4"),
        (28,"\nThese are your monthly habits: \n\nhabit: clean windows, streak: 1")
    ])

    def test_show_habits_by_periodicity(self, hm,clear_db, db_connection, periodicity, expected_message, test_habit1, test_habit2, test_habit3, test_habit4, test_habit5):

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

        #load fixture habits into the HabitManager instance
        #name of the habit : values of the corresponding habit objects
        hm.habits = {
            test_habit1.name: test_habit1,
            test_habit2.name: test_habit2,
            test_habit3.name: test_habit3,
            test_habit4.name: test_habit4,
            test_habit5.name: test_habit5
        }


        # update the values inside the database from the default values
        for habit in hm.habits.values():
            cur.execute(
                """INSERT OR REPLACE INTO habit (
                name,
                periodicity,
                streak,
                longest_streak,
                checked_off,
                creation_time,
                milestone) VALUES (?,?,?,?,?,?,?)""",
                (habit.name, habit.periodicity, habit.streak, habit.longest_streak, habit.checked_off, habit.creation_time.strftime('%Y-%m-%d %H:%M:%S'), habit.milestone)
            )
        conn.commit()

        # load habits from the database
        hm.load_habits_into_memory()

        
        #debug test
        cur.execute("SELECT name, streak FROM habit")
        print(cur.fetchall())
       

        # call show_habits_by_periodicity and assert the output
        assert hm.show_habits_by_periodicity(periodicity) == expected_message
        
    def test_show_all_habits(self, db_connection, clear_db, hm, test_habit1, test_habit2, test_habit3, test_habit4, test_habit5):

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

        #load fixture habits into the HabitManager instance
        #name of the habit : values of the corresponding habit objects
        hm.habits = {
            test_habit1.name: test_habit1,
            test_habit2.name: test_habit2,
            test_habit3.name: test_habit3,
            test_habit4.name: test_habit4,
            test_habit5.name: test_habit5
        }


        # update the values inside the database from the default values
        for habit in hm.habits.values():
            cur.execute(
                """INSERT OR REPLACE INTO habit (
                name,
                periodicity,
                streak,
                longest_streak,
                checked_off,
                creation_time,
                milestone) VALUES (?,?,?,?,?,?,?)""",
                (habit.name, habit.periodicity, habit.streak, habit.longest_streak, habit.checked_off, habit.creation_time.strftime('%Y-%m-%d %H:%M:%S'), habit.milestone)
            )
        conn.commit()

        # load habits from the database
        hm.load_habits_into_memory()

        # create the expected output
        expected_output = (
            "Here is the list of all your habits with their name , streak & periodicity in days:\n\n"
            f"habit: {test_habit1.name}, streak: {test_habit1.streak}, periodicity: {test_habit1.periodicity}\n"
            f"habit: {test_habit2.name}, streak: {test_habit2.streak}, periodicity: {test_habit2.periodicity}\n"
            f"habit: {test_habit3.name}, streak: {test_habit3.streak}, periodicity: {test_habit3.periodicity}\n"
            f"habit: {test_habit4.name}, streak: {test_habit4.streak}, periodicity: {test_habit4.periodicity}\n"
            f"habit: {test_habit5.name}, streak: {test_habit5.streak}, periodicity: {test_habit5.periodicity}\n"
        )

        # assert that the returned output matches the expected output
        assert hm.show_all_habits() == expected_output

    def test_longest_streak(self, hm, db_connection, clear_db, test_habit1, test_habit2, test_habit3, test_habit4, test_habit5):
        """ testing the if longest_streak returns the method with the longest streak """
        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

        #load fixture habits into the HabitManager instance
        #name of the habit : values of the corresponding habit objects
        hm.habits = {
            test_habit1.name: test_habit1,
            test_habit2.name: test_habit2,
            test_habit3.name: test_habit3,
            test_habit4.name: test_habit4,
            test_habit5.name: test_habit5
        }


        # update the values inside the database from the default values
        for habit in hm.habits.values():
            cur.execute(
                """INSERT OR REPLACE INTO habit (
                name,
                periodicity,
                streak,
                longest_streak,
                checked_off,
                creation_time,
                milestone) VALUES (?,?,?,?,?,?,?)""",
                (habit.name, habit.periodicity, habit.streak, habit.longest_streak, habit.checked_off, habit.creation_time.strftime('%Y-%m-%d %H:%M:%S'), habit.milestone)
            )
        conn.commit()

        # load habits into memory
        hm.load_habits_into_memory()

        # call longest_streak and store it in the variable result
        result = hm.longest_streak()

        assert result is not None
        assert result ['name'] == "drink 2l water"
        assert result ['longest_streak'] == 28

    def test_longest_streak_for_habit(self, db_connection, clear_db, hm, test_habit1, test_habit2, test_habit3, test_habit4, test_habit5):

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

        #load fixture habits into the HabitManager instance
        #name of the habit : values of the corresponding habit objects
        hm.habits = {
            test_habit1.name: test_habit1,
            test_habit2.name: test_habit2,
            test_habit3.name: test_habit3,
            test_habit4.name: test_habit4,
            test_habit5.name: test_habit5
        }


        # update the values inside the database from the default values
        for habit in hm.habits.values():
            cur.execute(
                """INSERT OR REPLACE INTO habit (
                name,
                periodicity,
                streak,
                longest_streak,
                checked_off,
                creation_time,
                milestone) VALUES (?,?,?,?,?,?,?)""",
                (habit.name, habit.periodicity, habit.streak, habit.longest_streak, habit.checked_off, habit.creation_time.strftime('%Y-%m-%d %H:%M:%S'), habit.milestone)
            )
        conn.commit()

        # load habits into memory
        hm.load_habits_into_memory()

        # assert that the expected output is displayed to the user when habits exist
        result = hm.longest_streak_for_habit("gym")
        assert result == "The longest streak for the habit 'gym' is : 14\n"
        result = hm.longest_streak_for_habit("cardio")
        assert result == "The longest streak for the habit 'cardio' is : 7\n"
        result = hm.longest_streak_for_habit("visit grandma")
        assert result == "The longest streak for the habit 'visit grandma' is : 4\n"
        result = hm.longest_streak_for_habit("drink 2l water")
        assert result == "The longest streak for the habit 'drink 2l water' is : 28\n"
        result = hm.longest_streak_for_habit("clean windows")
        assert result == "The longest streak for the habit 'clean windows' is : 1\n"

        # assert that the expected output is displayed to the user when a habit doesn't exist
        result = hm.longest_streak_for_habit("nonexistent_habit")
        assert result == "No habit with the name nonexistent_habit exists - please enter the correct name.\n"


    def test_missed_counter(self, hm, db_connection, clear_db, test_habit1, test_habit2):
        """ testing if missed_counter correctly counts all missed times """

        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

        # define a fixed date for testing
        fixed_now = datetime(2025,2,1,12,0,0)
        interval_30_days = (fixed_now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

        # create missed time logs for test_habit1
        missed_times = [
            (test_habit1.name, (fixed_now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit1.name, (fixed_now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit1.name, (fixed_now - timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S'))
        ]

        # insert the missed times into the database
        cur.executemany(
            "INSERT INTO reset_log (name, missed_time) VALUES (?,?)", missed_times
        )
        conn.commit()

        # mock datetime.now() to use fixed_now instead
        with patch("habit_manager.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now

            # test 1 : habit with 3 missed times in the last 30 days
            assert hm.missed_counter(test_habit1.name) == 3

            # test 2 : in case a habit doesn't exist anymore but a query is still made -> should return 0
            assert hm.missed_counter("nonexisting_habit") == 0

            # test 3 : habit has a missed time but it is 40 days ago
            cur.execute(
                "INSERT INTO reset_log (name, missed_time) VALUES (?,?)", ("old_habit", (fixed_now - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S'))
            )

            conn.commit()
            assert hm.missed_counter("old_habit") == 0

            # test 4 : habit has no missed times
            assert hm.missed_counter(test_habit2.name) == 0

    def test_most_misses(self, hm, db_connection, clear_db, test_habit1, test_habit2, test_habit4):
        """ testing if most_misses correctly displays the habit with the most misses """
        # unpack the tuple of connection and cursor
        conn, cur = db_connection

        # set the database name
        hm.db_name = "test.db"

         # update the values inside the database from the default values
        for habit in hm.habits.values():
            cur.execute(
                """INSERT OR REPLACE INTO habit (
                name,
                periodicity,
                streak,
                longest_streak,
                checked_off,
                creation_time,
                milestone) VALUES (?,?,?,?,?,?,?)""",
                (habit.name, habit.periodicity, habit.streak, habit.longest_streak, habit.checked_off, habit.creation_time.strftime('%Y-%m-%d %H:%M:%S'), habit.milestone)
            )
        conn.commit()

        # load habits into memory
        hm.load_habits_into_memory()

        # create a fixed datetime 
        fixed_now = datetime(2025,2,7,10,0,0)

        # create mocked missed_times for the test_habits
        missed_times = [

            # missed times for test_habit1
            (test_habit1.name, (fixed_now - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit1.name, (fixed_now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit1.name, (fixed_now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')),

            # missed times for test_habit2
            (test_habit2.name, (fixed_now - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit2.name, (fixed_now - timedelta(days=12)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit2.name, (fixed_now - timedelta(days=28)).strftime('%Y-%m-%d %H:%M:%S')),

            # missed times for test_habit 4
            (test_habit4.name, (fixed_now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit4.name, (fixed_now - timedelta(days=16)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit4.name, (fixed_now - timedelta(days=19)).strftime('%Y-%m-%d %H:%M:%S')),
            (test_habit4.name, (fixed_now - timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S'))
        ]

        # insert the missed_times into the reset_log table
        for name, missed_time in missed_times:
            cur.execute(
                "INSERT INTO reset_log (name, missed_time) VALUES (?,?)", (name, missed_time)
            )
        conn.commit()

        # mock the datetime to use fixed_now instead
        with patch("habit_manager.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now

            # call most_misses()
            result = hm.most_misses()

            # assert that the result is the habit with the most missed times 
            assert result == f"The habit you struggled the most with was '{test_habit4.name}' with '4' missed times.\n"


