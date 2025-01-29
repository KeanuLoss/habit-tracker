from datetime import datetime, timedelta
import sqlite3

class Habits:
    def __init__(self, name, periodicity, streak = 0, milestone = 0, missed_time = None, longest_streak = 0, creation_time = None, checked_off = False):
        self.name = name
        self.periodicity = periodicity
        self.streak = streak
        self.milestone = milestone
        # if creation time is none, set it to the current time
        self.creation_time = creation_time or datetime.now()
        self.longest_streak = longest_streak
        self.missed_time = missed_time
        self.checked_off = checked_off
        

    def __str__(self):
        return (f"Periodicity : {self.periodicity}, Streak: {self.streak}, Last Checked: {self.missed_time}")
    

    def check_off(self):
        """ checks off a habit """
        self.checked_off = True # changes the status of the habit to "checked off"
        if self.is_within_current_period():
            self.streak += 1
            self.checked_off = True
            print(f"Awesome! You are on a {self.streak} day streak - keep going ! ")
            if self.streak > self.longest_streak:
                self.longest_streak = self.streak
        else:
            self.streak = 1
            print(f"You missed your streak, your streak is at 1 again - I know you will do better this time, you've got this ! ")
        


    def increment_milestone(self):
        """ increments the milestone value """
        if self.streak % 7 == 0 :
            self.milestone += 1
            print(f"YAAAY - you've managed to hit a milestone ! You checked off {self.name} {self.streak} times in a row, you can be proud of your dedication ! Keep going and get the next milestone ! ")
        


    def reset_checked_off(self):
        """ Resets the checked-off status and handles updating the streak or missed_count """
        # calculate the end of the current period
        elapsed_time = datetime.now() - self.creation_time
        period_length = timedelta(days = self.periodicity)
    
        # calculate the start and end of the current period
        periods_elapsed = elapsed_time // period_length
        current_period_start = self.creation_time + periods_elapsed * period_length
        current_period_end = current_period_start + period_length
    


        # check if the tasked is checked off in the set period
        if datetime.now() >= current_period_end:
            if not self.checked_off:
                # reset the streak if the current time is outside the current periodicity and checked_off was False
                self.streak = 0

                # log the reset time in the database
                with sqlite3.connect(self.db_name) as db:
                    cur = db.cursor()
                    cur.execute(
                        """ 
                        INSERT INTO reset_log (habit_name,missed_time)
                        VALUES (?,?)
                    """, (habit.name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    )
                    db.commit()

        # reset checked_off back to false when the the current time is within the current period and checked_off is True
        if  current_period_start <= datetime.now() <= current_period_end:
            self.checked_off = False 

    
        # update the habit data in the database
        with sqlite3.connect(self.db_name) as db:
            cur = db.cursor()
            cur.execute(
                """
                UPDATE habit
                SET streak = ?, checked_off =?
                WHERE name =?
            """, (self.missed_count, self.streak, self.checked_off, habit.name))

            db.commit()
        

    def is_within_current_period(self):
        """ check if the current time is within the current period """
        #calculating the time that has elapsed
        elapsed_time = datetime.now() - self.creation_time

        #calculating the periodicity as a timedelta
        period_length = timedelta(days=self.periodicity)

        #calculating the start of the current period
        periods_elapsed = elapsed_time // period_length
        current_period_start = self.creation_time + periods_elapsed * period_length

        #calculating the end of the current period
        current_period_end = current_period_start + period_length 

        # checking if the current time is within the current period
        return current_period_start <= datetime.now() < current_period_end
    


        
    

