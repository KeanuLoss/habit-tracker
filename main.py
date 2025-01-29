import threading
import time
from habit_manager import HabitManager          #imports the logic for habit management
from predefined_habits import PredefinedHabits  #imports the logic for the predefined habits
from GUI import TextRedirector, HabitGUI  #imports the GUI
import tkinter as tk



def main(habit_manager):

    # create the main application window
    root = tk.Tk()

    # initialize the backend 
    habit_manager = HabitManager()
    predefined_habits = PredefinedHabits()

    # initialize the HabitGUI with the root window
    app = HabitGUI(root, habit_manager, predefined_habits)

    # load all habits into the memory
    habit_manager.load_habits_into_memory()


    
    # start the TKinter event loop
    root.mainloop()


def background_reset_task(habit_manager):
    """ task that runs in the background to reset checked_off back to False when a new period started """
    while True:
        # reset all habits in the HabitManager
        habit_manager.reset_all_habits()
        # waits for 1800seconds ( 30 minutes )
        time.sleep(1800) 



if __name__ == "__main__":
    # create an instance of HabitManager
    habit_manager = HabitManager()

    """ start the background task for resetting the tasks when a new period started in a seperate thread """
    reset_thread = threading.Thread(target=background_reset_task, args =(habit_manager,), daemon = True)
    reset_thread.start()


    # pass habit_manager to main
    main(habit_manager)


    
    
