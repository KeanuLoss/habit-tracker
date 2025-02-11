from apscheduler.schedulers.background import BackgroundScheduler
from habit_manager import HabitManager          #imports the logic for habit management
from GUI import HabitGUI  #imports the GUI
import customtkinter as ctk


def scheduled_reset(habit_manager):
    """ function that resets all habits at the end of the day """
    for habit in habit_manager.habits.values():
        habit.reset_checked_off()

def main():

    # initialize the backend with the db_name specified, either test.db for testing or habit.db for the actual program
    habit_manager = HabitManager("habit.db")

    # initialize the database
    habit_manager.initialize_database()
    
    # load all habits into the memory
    habit_manager.load_habits_into_memory()

    # create the main application window
    root = ctk.CTk()

    # initialize the HabitGUI with the root window
    app = HabitGUI(root, habit_manager)

    # setting up the scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_reset, 'cron', hour = 23, minute = 59, second = 57, args = [habit_manager])
    scheduler.start()

    try:
        # start the TKinter event loop
        # this blocks every other code from running until the GUI is closed
        root.mainloop()
    except KeyboardInterrupt:
        scheduler.shutdown()

if __name__ == "__main__":
   
   #when the file is run directly -> call the main() function 
   main()

    

    
    
