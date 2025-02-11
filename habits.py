from datetime import datetime, timedelta, time
import sqlite3

class Habits:
    def __init__(self, name, periodicity, streak = 0, milestone = 0, missed_time = None, longest_streak = 0, creation_time = None, checked_off = 0, db_name = "test.db"):
        self.name = name
        self.periodicity = periodicity
        self.streak = streak
        self.milestone = milestone
        self.creation_time = creation_time or datetime.now()
        self.longest_streak = longest_streak
        self.missed_time = missed_time
        self.checked_off = checked_off
        self.db_name = db_name

    def __str__(self):
        """ turns the habit objects into a readable string """
        return (f"Periodicity : {self.periodicity}, Streak: {self.streak}, Last Checked: {self.missed_time}")
    
    def check_off(self):
        """ checks off a habit """
        if self.checked_off == 1:
            return f"You already checked off your habit - good job! Now let's work on your other habits :)\n"
        
    
        self.streak += 1
        self.checked_off = 1

        if self.streak > self.longest_streak:
            self.longest_streak = self.streak

        return f"You checked off the habit '{self.name}'.\n Awesome! You are on a {self.streak} day streak - keep going ! \n"
        
    def increment_milestone(self):
        """ increments the milestone value """
        if self.streak % 7 == 0 :
            self.milestone += 1
            return f"YAAAY - you've managed to hit a milestone! You checked off {self.name} {self.streak} times in a row, you can be proud of your dedication! Keep going and get the next milestone!\n"
        
        # return an empty string when no milestone is reached
        return ""

    def reset_checked_off(self):
        """ Resets the checked-off status and handles updating the streak or creating a log for missed_time """
        # convert the creation_time from a string back into a datetime object
        if isinstance(self.creation_time, str):
            self.creation_time = datetime.strptime(self.creation_time,"%Y-%m-%d %H:%M:%S")

        
        # calculate the end of the current period (creation_time + periodicity)
        # convert periodicity "number of days" into an integer
        period_end = self.creation_time + timedelta(days=int(self.periodicity))

        # Get the current time
        current_time = datetime.now()

        # check if the current date 'current_time.date()' is equal to the period end and if the habit is not checked off
        if current_time.date() == period_end.date():
            if self.checked_off == 0:

                # reset the streak
                self.streak = 0
                self.milestone = 0

                
                with sqlite3.connect(self.db_name) as db:
                    cur = db.cursor()

                    #log the missed time
                    cur.execute(
                        """
                        INSERT INTO reset_log (name, missed_time)
                        VALUES (?,?)
                        """, (self.name, current_time.strftime('%Y-%m-%d %H:%M:%S'))
                    )
                    

                    # update the creation_time to correctly calculate the next period end
                    cur.execute(
                        """UPDATE habit
                        SET creation_time = ?, streak = ?, milestone = ? 
                        WHERE name = ?""", (period_end.strftime('%Y-%m-%d %H:%M:%S'), self.streak, self.milestone, self.name)
                    )

                    db.commit()

            # if the habit has been checked off :
            elif self.checked_off == 1:
                # reset the check off so the habit can be checked off in the new period
                self.checked_off = 0

            # update the check_off value and creation_time to correctly calculate the next period end
            with sqlite3.connect(self.db_name) as db:
                cur = db.cursor()
                cur.execute(
                    """
                    UPDATE habit
                    SET creation_time = ?, checked_off = ?
                    WHERE name = ?""", (period_end.strftime('%Y-%m-%d %H:%M:%S'), self.checked_off, self.name)
                )
                db.commit()


    
        
        
    


        
    

