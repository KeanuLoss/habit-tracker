import tkinter as tk
from tkinter import messagebox,StringVar
from habit_manager import HabitManager
from predefined_habits import PredefinedHabits
import sys



class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Auto-scroll to the end

    def flush(self):
        pass  # No-op to satisfy the interface


class HabitGUI:
    def __init__(self, root, habit_manager, predefined_habits):
        self.root = root
        self.root.title("Habit Tracker")
        self.habit_manager = habit_manager  # Backend instance
        self.predefined_habits = predefined_habits
        self.create_widgets()
        self.redirect_stdout()
        self.selected_value = StringVar()

    def create_widgets(self):
        """Set up the GUI layout and components."""
        # Display area
        self.display_area = tk.Text(self.root, height=20, width=100)
        self.display_area.pack(pady=10)

        # Buttons on the right side
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        tk.Button(button_frame, text="+ Create New Habit", command=self.create_new_habit).pack(pady=5)
        tk.Button(button_frame, text="- Delete Habit", command=self.delete_habit).pack(pady=5)
        tk.Button(button_frame, text="Check Off Habit", command=self.check_off_habit_window).pack(pady=5)
        tk.Button(button_frame, text="Analyze Habits", command=self.analyze_habits).pack(pady=5)
    

    def redirect_stdout(self):
        """ Redirect the terminal to the display area. """
        sys.stdout = TextRedirector(self.display_area)
        sys.stderr = TextRedirector(self.display_area)

    def update_display(self, message):
        """Update the display area with a message."""
        self.display_area.insert(tk.END, message + "\n")
        self.display_area.see(tk.END)

    def create_new_habit(self):
        """Handle creating a new habit."""
        def submit():
            name = name_entry.get()  # get the name-value entered by the user in the name_entry widget and store it in the variable name
            periodicity = periodicity_var.get()  # get the periodcity-value from the user and store it in the variable periodicity
            # retrieve the custom periodicity from the user
            custom_periodicity = custom_periodicity_entry.get()

            #check if a custom periodicity is provided
            if custom_periodicity:
                if custom_periodicity.isdigit() and int(custom_periodicity) > 0:
                    periodicity_var.set(int(custom_periodicity)) 
                else:
                    tk.messagebox.showerrer("Invalid input - please enter a valid number between 1 and 365.")

            try:
                # make sure the that periodicity is stored as an integer
                periodicity = int(periodicity) 
            except ValueError:
                messagebox.showerror("Invalid input", "Periodicity must be a valid number between 1 and 365.")
                return

            if name and periodicity > 0:
                try:
                    self.habit_manager.add_habit(name, periodicity)
                    self.update_display(f"Habit '{name}' created with periodicity '{periodicity}'.")
                    new_habit_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showwarning("Input Required", "Please provide both name and periodicity.")

        new_habit_window = tk.Toplevel(self.root)
        new_habit_window.title("Create New Habit")

        tk.Label(new_habit_window, text="Habit Name:").pack(pady=5)
        name_entry = tk.Entry(new_habit_window)
        name_entry.pack(pady=5)

        tk.Label(new_habit_window, text="Periodicity in days:").pack(pady=5)
        # the default value for periodicity is -1 so no radio button is selected
        periodicity_var = tk.StringVar(value="-1")
        predefined_frame = tk.Frame(new_habit_window)
        predefined_frame.pack(pady=5)

        # buttons for the predefined periods daily, weekly and monthly
        tk.Radiobutton(predefined_frame, text="daily", variable = periodicity_var, value="1").pack(anchor=tk.W)
        tk.Radiobutton(predefined_frame, text="weekly", variable = periodicity_var, value = "7").pack(anchor=tk.W)
        tk.Radiobutton(predefined_frame, text="monthly", variable = periodicity_var, value = "28").pack(anchor=tk.W)

        # entry for custom periods
        tk.Label(new_habit_window, text = "Or enter any period of your choice in days").pack(pady=5)
        custom_periodicity_entry = tk.Entry(new_habit_window)
        custom_periodicity_entry.pack(pady=5)

        def update_periodicity_from_entry(*args):
            value = custom_periodicity_entry.get()
            if value.isdigit() and int(value) > 0:
                periodicity_var.set(int(value))
            elif not value:
                periodicity_var.set(0)

        # bind the custom input changes to periodicity_var
        custom_periodicity_entry.bind("<KeyRelease>", update_periodicity_from_entry)


        tk.Button(new_habit_window, text="create your new habit", command=submit).pack(pady=10)

    def delete_habit(self):
        """Handle deleting a habit."""
        def submit():
            name = name_entry.get()
            if name:
                try:
                    self.habit_manager.delete_habit(name)
                    self.update_display(f"Habit '{name}' deleted.")
                    delete_habit_window.destroy()
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showwarning("Input Required", "Please enter a habit name.")

        delete_habit_window = tk.Toplevel(self.root)
        delete_habit_window.title("Delete Habit")

        tk.Label(delete_habit_window, text="Habit Name:").pack(pady=5)
        name_entry = tk.Entry(delete_habit_window)
        name_entry.pack(pady=5)

        tk.Button(delete_habit_window, text="Delete", command=submit).pack(pady=10)

    def check_off_habit_window(self):
        """ creates the window for checking off a habit """
        def check_action():
            # get the habit name from the entry box
            habit_name = entry.get().strip()
            # make sure a habit name was entered
            if not habit_name:
                tk.messagebox.showerror("Error, please enter the name of a habit. ")
                return
            
            try:
                # call the check_off_habit method from the HabitManager class
                self.habit_manager.check_off_habit(habit_name)

                
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))
           
        # create a new window for checking off habits
        check_window = tk.Toplevel(self.root)
        check_window.title("Check Off Habit")

        # add the widgets to the new window
        tk.Label(check_window, text="Enter the name of the habit you just finished").pack(pady=10)
        entry = tk.Entry(check_window, width=30)
        entry.pack(pady=5)
        tk.Button(check_window, text="habit finished", command=check_action).pack(pady=10)


    

    def show_all_habits(self):
        habits = self.habit_manager.get_all_habits()
        if not habits:
            print("You currently don't have any habits that you're trying to build.")
            return
        print("These are all your habits with their periodicity and current streak:")
        for name, details in habits.items():
            print(f"{name}: {details}")

   

    def show_habits(self,periodicity):
        """  displays the habits based on the selected periodicity  """
        message = self.habit_manager.show_habits_by_periodicity(periodicity)
        self.update_display(message)

        
    def analyze_habits(self):
           

        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Analyze Habits")
        
        #buttons for the different periodicites
        tk.Button(analysis_window, text="Show All My Habits", command = self.show_all_habits).pack(pady=5)
        tk.Button(analysis_window, text="Show All Daily Habits", command= lambda: self.show_habits(1)).pack(pady=5)
        tk.Button(analysis_window, text="Show All Weekly Habits", command=lambda: self.show_habits(7)).pack(pady=5)
        tk.Button(analysis_window, text="Show All Monthly Habits", command=lambda: self.show_habits(28)).pack(pady=5)


        def display_most_misses():
            """ prints the habits that was missed to be checked off the most """
            result = self.habit_manager.most_misses()
            print(result)  # Debugging: Ensure the returned string is printed
            

        #button for " what did I struggle with the most"
        tk.Button(analysis_window, text="What Habit Did I Struggle With the Most Last Month", command=display_most_misses).pack(pady=5)

        def display_longest_streak():
            """ prints the habit with the longest streak """
            result = self.habit_manager.longest_streak()
            if result is None:
                print("No habits found.")
            else:
                print(f"Your longest streak is {result['longest_streak']} for the habit '{result['name']}'.")

        
        #button for longest streak
        tk.Button(analysis_window, text="Show the Habit with the Longest Streak", command = display_longest_streak).pack(pady=5)


        def display_longest_streak_for_habit():
            """ prints the longest streak for a specific habit  """
            habit_name = self.habit_manager.longest_streak_for_habit()

        def open_streak_window():
            streak_window = tk.Toplevel(analysis_window)
            streak_window.title("Find Streak")
            # label for user instruction
            tk.Label(streak_window, text="Enter the name of the habit you want to see your streak of").pack(pady=10)
            
            # opens the field for user input 
            entry = tk.Entry(streak_window, width=30)
            entry.pack(pady=5)

            # button to find the streak
            tk.Button(streak_window, text="Find Streak", command=lambda: self.habit_manager.longest_streak_for_habit(entry.get())).pack(pady=10)

        tk.Button(analysis_window, text="Show the Longest Streak for a Specific Habit", command=open_streak_window).pack(pady=5)



        

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitGUI(root)
    root.mainloop()



