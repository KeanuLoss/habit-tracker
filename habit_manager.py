import sqlite3
from datetime import datetime, timedelta
from habits import Habits

class HabitManager:
    def __init__(self,db_name="habit.db"):
        self.habits = {}
        self.db_name = db_name
        self.initialize_database()
        
    
    def initialize_database(self):
        """ creates the habit and reset_log table if it doesn't exist in the database """
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            # this creates the table that stores the habit details
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS habit(name TEXT PRIMARY KEY,
                        periodicity INTEGER NOT NULL,
                        streak INTEGER DEFAULT 0,
                        longest_streak INTEGER DEFAULT 0,
                        checked_off INTEGER DEFAULT 0, 
                        creation_time TEXT,
                        milestone INTEGER DEFAULT 0
                         )""")
            # this creates the table that stores the dates when a habit was missed to check off in time       
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS reset_log(
                name TEXT PRIMARY KEY,
                missed_time TEXT DEFAULT NULL,
                FOREIGN KEY (name) REFERENCES habit (name))"""
            )
            db.commit()

    
    def load_habits_into_memory(self):
        """ loads all habits from the database into memory """
        #fetch all the required habit details from the habits table 
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM habit") # select everything
            habits = cur.fetchall()

        # clear existing in-memory storage
        self.habits.clear()


        # fill the in-memory storage with instances of the Habit class by looping 
        for name, periodicity, streak, longest_streak, checked_off, creation_time, milestone in habits:
            
 
            habit = Habits(
                name = name,
                periodicity = int(periodicity),
                streak = int(streak),
                longest_streak = int(longest_streak),
                checked_off = bool(checked_off),
                creation_time = creation_time,
                milestone = int(milestone)  
            )
            self.habits[name] = habit

    def add_habit(self,name,periodicity):
        """ adds a new habit and periodicity to the in-memory list and the database """

        # convert the name to lowercase
        normalized_name = name.lower()

        #check if the name of the habit already exists
        if self.habit_exists(normalized_name):
            raise ValueError(f"You already have a habit with the name '{name}'. \n Please choose another name for the habit you want to add.")
        
        # ensure that the periodicity is of type integer
        try : 
            periodicity = int(periodicity)
        except ValueError:
            raise ValueError("The periodicity must be entered as a number of days.")
        
        #create an instance of Habit
        creation_time = datetime.now()
        new_habit = Habits(name=name, periodicity=periodicity, streak= 0, creation_time = creation_time, checked_off = False, milestone = 0 )

        # add to the in-memory storage
        self.habits[normalized_name] = new_habit
        
        # add to the database
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            try:
                # add to the habit table
                cur.execute('''
                               INSERT INTO habit (
                            name,
                            periodicity,
                            streak,
                            longest_streak,
                            checked_off,
                            creation_time,
                            milestone)
                             VALUES (?,?,?,?,?,?,?)''',
                               (new_habit.name, new_habit.periodicity, 0, 0,0, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 0)) # isoformat converts the datetine.now() into a string
                

            
            # exception that prevents a crash when the name already exists
            except sqlite3.IntegrityError: 
                print(f"Habit '{name}' already exists in the database. Please enter another name for your habit.")


    def delete_habit(self,name):
        """ deletes the habit and the periodicity from the memory and the database """

        # convert the input name to lowercase
        normalized_name = name.lower()

        # check if the entered name exists
        if normalized_name not in self.habits:
            raise ValueError(f"No habit with the name '{name}' exists.")
        
        # remove from the in-memory list
        del self.habits[normalized_name]

        # remove habit from the database
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            
            #normalize the name in the database as well 
            cur.execute('DELETE FROM habit WHERE LOWER(name) = ?', (normalized_name,))
            cur.execute('DELETE FROM reset_log WHERE LOWER(name) = ?', (normalized_name,))
            db.commit()

                    

    def check_off_habit(self,name):
        """ identifies and validates the habit in the collection & database """

        # check if the entered habit name exists
        if not self.habit_exists(name):
            raise ValueError(f"No habit with the name '{name} exists.")
        
        # get the habit object and check it off
        habit = self.habits[name]
        habit.check_off() 
        habit.increment_milestone()
        missed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # update the habit in the database
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            cur.execute("""
                UPDATE habit
                SET streak = ?, longest_streak = ?
                WHERE name = ?
            """,
            #WHERE name = ? ensures that only the row corresponding to the habit being checked off is updated 
            (habit.streak, habit.longest_streak, name))
            db.commit()

        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            cur.execute(
                """
                UPDATE reset_log
                SET missed_time = ?
                WHERE name = ?
                """, (missed_time, name)
            )
            db.commit()

    
    def get_all_habits(self):
        return {name: {"periodicity" : habit.periodicity, "streak" : habit.streak} for name, habit in self.habits.items()}
    
    def periodicity_to_text(self, periodicity):
        """ converts the periodicity value chosen by the user into a readable text  """
        #
        mapping = {
            1 : "daily",
            7 : "weekly",
            28 : "monthly"
        }
        return mapping.get(periodicity,"unknown")

    def show_habits_by_periodicity(self,periodicity):
        """ shows all habits with the same periodicity """
        #reload habits from the database
        self.load_habits_into_memory()
        # filter all habits by periodicity and include the name as well as the streak
        habits = [(name, habit.streak) for name, habit in self.habits.items() if habit.periodicity == periodicity]
        #check if the dictionary "habits" is empty which would make the result "False" 
        if not habits:
            return(f"You don't have any {self.periodicity_to_text(periodicity)} habits yet - go change that!")
        return "\n".join([f" These are your {self.periodicity_to_text(periodicity)} habits : \n Habit: {name}, Streak: {streak}" for name, streak in habits])    
        # create a dictionary for the different periodicities 


 
    def show_all_habits(self):
        """ shows all habits """
        #reload habits into memory
        self.load_habits_into_memory()
        # store the dictionary in the variable habits
        habits = self.get_all_habits()
        if not habits:  # if it's true that habits is empty 
            print("No habits to analyze.")
            return
        print("Here is a list of all your habits:")  # when habits is not empty 

        # iterate through the items of the dictionary habits 
        for name, streak in habits.items():
            print(f"habit : {name} streak : {streak}")


    def longest_streak(self):
        """ displays the longest streak of all habits """
        # iterate through the in-memory storage to work with the latest state of data
        # make sure that habits are loaded
        if not self.habits:
            return None
      
        # find the habit with the longest streak
        # the max function finds the maximum element in a collection based on a criterion by comparing the values the lambda function returns 
        # key = lambda habit : a function that takes a single argument (habit) and returns the longest_streak attribute of the habit object
        longest_streak_habit = max(self.habits.values(), key = lambda habit: habit.longest_streak) 
        return {
            'name' : longest_streak_habit.name,
            'longest_streak' : longest_streak_habit.longest_streak
        }
    
    def longest_streak_for_habit(self,name):
        """ displays the longest streak for a speficic habit """

        # convert the name to lowercase
        normalized_name = name.lower()

        # check if the habit exists
        if not self.habit_exists(normalized_name):
            print(f"No habit with the name {name} exists - please enter the correct name.")
            return
        
        # retrieve the habit from the in-memory storage
        habit = self.habits.get(normalized_name)

        # print the longest streak 
        print(f"The longest streak for the habit '{name}' is : {habit.longest_streak}")
        

    def habit_exists(self,name):
        """ checks if a habit exists """
        return name in self.habits

    def reset_all_habits(self):
        """ calls the reset_checked_off method on all habits """
        # iterate over the habit objects and call reset_checked_off on them 
        for habit in self.habits.values() :
            habit.reset_checked_off()
           


    def missed_counter(self, habit_name):
        """ counts how often a streak was reset in the past 30 days """
        # calculate the interval of the past 30 days
        interval_30_days = datetime.now() - timedelta(days=30).strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()

            # query how many times a habit wasn't checked off in the set periodicity
            cur.execute(
                """ SELECT COUNT(*)
                FROM reset_log
                WHERE name = ?
                AND missed_time >= ?
            """, (habit_name,interval_30_days)
            )

            # fetch the count from the query
            result = cur.fetchone()
            if not result:
                raise ValueError(f"No Habit found with the name '{habit_name}'.")
            


    def most_misses(self):
        """ finds the habit with the most missed_time logs in the past 30 days """

        
        # calculate the start of the 30 day interval
        interval_30_days = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()

            # query to count the missed_time logs for each habit in the last 30 days
            cur.execute(
                """
                SELECT name, COUNT(*) as missed_count
                FROM reset_log
                WHERE missed_time >= ?
                GROUP BY name
                ORDER BY missed_count DESC
                LIMIT 1
                """, (interval_30_days,) # trailing comma is necessary because a tuple is required, otherwise it will be interpreted as a string instead of a tuple
            )
                        
            # fetch the result ( habit name and the count )
            result = cur.fetchone()


            if result is None:
                return "You're doing great ! You've never missed one of your habits in the past 30 days - I'm so proud of you !"
        
        # unpack the result to print the value
        habit_name, missed_count = result 
        return f"The habit you struggled the most with was '{habit_name}' with '{missed_count} missed times."
          

