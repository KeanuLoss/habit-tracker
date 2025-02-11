import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import tkinter as tk
from tkinter import messagebox,StringVar
from habit_manager import HabitManager
import sys


class HabitGUI:
    def __init__(self, root, habit_manager):
        self.root = root
        self.root.geometry("800x600+550+200")
        self.root.title("Habit Tracker")
        self.habit_manager = habit_manager  # store the HabitManager instance
        self.create_widgets()
        self.selected_value = StringVar()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.display_area = ctk.CTkTextbox(self.root, height=300, width=600)
        self.display_area.pack(padx=15, pady=10)

    
    def update_display(self, message):
        """ Update the display area with a message """
        self.display_area.insert("end", message + "\n")
        self.display_area.see("end")
        self.display_area.update_idletasks()

    def clear_display(self):
        """ clears the display area """
        self.display_area.delete("1.0", "end")

    def create_widgets(self):
        """  Set up the GUI layout and components """

        # Buttons on the right side
        button_frame = ctk.CTkFrame(self.root, fg_color="gray15", corner_radius=10, width=200, height=250)
        button_frame.pack(side="right", padx=(0,20), pady=(10,0), anchor="ne")

        button_font = ("Arial", 14)

        # button for creating a new habit
        ctk.CTkButton(button_frame, text="+ create new habit", command=self.create_new_habit, font=button_font, fg_color="royalblue").pack(pady=5)
        # button for deleting a habit
        ctk.CTkButton(button_frame, text="- delete habit", command=self.delete_habit,font=button_font, fg_color="royalblue").pack(pady=5)
        # button for checking off a habit
        ctk.CTkButton(button_frame, text="check off habit", command=self.check_off_habit_window,font=button_font, fg_color="royalblue").pack(pady=5)
        # button for analyzing habits
        ctk.CTkButton(button_frame, text="analyze habits", command=self.analyze_habits,font=button_font, fg_color="royalblue").pack(pady=5)
        # button for clearing the display area
        ctk.CTkButton(button_frame, text="clear display", command=self.clear_display,font=button_font, fg_color="royalblue").pack(pady=5)
        
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
                    CTkMessagebox(title="Error", message="Invalid input - please enter a valid number between 1 and 365.")

            try:
                # make sure the that periodicity is stored as an integer
                periodicity = int(periodicity) 
            except ValueError:
                CTkMessagebox("Invalid input", message="Periodicity must be a valid number between 1 and 365.")
                return

            if name and periodicity > 0:
                try:
                    self.habit_manager.add_habit(name, periodicity)
                    self.update_display(f"The habit '{name}' was successfully created with a periodicity of '{periodicity}'.\n")
                    new_habit_window.destroy()
                except ValueError as e:
                    CTkMessagebox(title="Error", message=str(e))
            else:
                CTkMessagebox(title="Warning", message="Input Required. Please provide both name and periodicity.")

        # create the window using customtkinter
        new_habit_window = ctk.CTkToplevel(self.root)
        new_habit_window.title("create a new habit")
        new_habit_window.geometry("400x350+750+570")

        # Keep the new window on top temporarily
        new_habit_window.attributes("-topmost", True)
        new_habit_window.after(100, lambda: new_habit_window.attributes("-topmost", False))

        # ensure background matches the theme
        new_habit_window.configure(fb_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

        button_font = ("Arial", 14)

        ctk.CTkLabel(new_habit_window, text="please enter the name of the habit you want to build:").pack(pady=5)
        name_entry = ctk.CTkEntry(new_habit_window)
        name_entry.pack(pady=5)

        ctk.CTkLabel(new_habit_window, text="periodicity in days:").pack(pady=5)
        # the default value for periodicity is -1 so no radio button is selected
        periodicity_var = ctk.StringVar(value="-1")
        predefined_frame = ctk.CTkFrame(new_habit_window, fg_color="transparent")
        predefined_frame.pack(pady=5)

        # buttons for the predefined periods daily, weekly and monthly
        ctk.CTkRadioButton(predefined_frame, text="daily", variable = periodicity_var, value="1").pack(anchor="w")
        ctk.CTkRadioButton(predefined_frame, text="weekly", variable = periodicity_var, value = "7").pack(anchor="w")
        ctk.CTkRadioButton(predefined_frame, text="monthly", variable = periodicity_var, value = "28").pack(anchor="w")

        # entry window for custom periods
        ctk.CTkLabel(new_habit_window, text = "or enter any period of your choice in days").pack(pady=5)
        custom_periodicity_entry = ctk.CTkEntry(new_habit_window)
        custom_periodicity_entry.pack(pady=5)

        def update_periodicity_from_entry(*args):
            value = custom_periodicity_entry.get()
            if value.isdigit() and int(value) > 0:
                periodicity_var.set(int(value))
            elif not value:
                periodicity_var.set(0)

        # bind the custom input changes to periodicity_var
        custom_periodicity_entry.bind("<KeyRelease>", update_periodicity_from_entry)


        ctk.CTkButton(new_habit_window, text="create your new habit", command=submit,font=button_font, fg_color="royalblue").pack(pady=10)

    def delete_habit(self):
        """Handle deleting a habit."""
        def submit():
            name = name_entry.get()
            if name:
                try:
                    message = self.habit_manager.delete_habit(name)
                    self.update_display(message)
                    delete_habit_window.destroy()
                except ValueError as e:
                    CTkMessagebox(title="Error", message= str(e))
            else:
                CTkMessagebox(title="Error", message= "Input required, please enter a habit name.")

        delete_habit_window = ctk.CTkToplevel(self.root)
        delete_habit_window.title("delete habit")
        delete_habit_window.geometry("300x150+800+570")

        # Keep the new window on top temporarily
        delete_habit_window.attributes("-topmost", True)
        delete_habit_window.after(100, lambda: delete_habit_window.attributes("-topmost", False))

        ctk.CTkLabel(delete_habit_window, text="Enter the name of the habit you want to delete:").pack(pady=5)
        name_entry = ctk.CTkEntry(delete_habit_window)
        name_entry.pack(pady=5)

        button_font = ("Arial", 14)

        ctk.CTkButton(delete_habit_window, text="delete habit", command=submit,font=button_font, fg_color="royalblue").pack(pady=10)

    def check_off_habit_window(self):
        """ creates the window for checking off a habit """
        def check_action():
            # get the habit name from the entry box
            habit_name = entry.get().strip()
            # make sure a habit name was entered
            if not habit_name:
                CTkMessagebox(title="Error", message= "Please enter the name of a habit that you want to check off. ")
                return
            
            try:
                # capture the message from the check_off method
                message = self.habit_manager.check_off_habit(habit_name)
                
                if message:
                    self.update_display(message)
                    
                else:
                    self.update_display("no message returned from check_off_habit")
                
                    
            except ValueError as e:
                CTkMessagebox(title="Error", message= str(e))
           
        # create a new window for checking off habits
        check_window = ctk.CTkToplevel(self.root)
        check_window.title("check off habit")
        check_window.geometry("300x200+800+570")

        # Keep the new window on top temporarily
        check_window.attributes("-topmost", True)
        check_window.after(100, lambda: check_window.attributes("-topmost", False))

        button_font = ("Arial", 14)

        # add the widgets to the new window
        ctk.CTkLabel(check_window, text="Enter the name of the habit you just finished").pack(pady=10)
        # window for user input
        entry = ctk.CTkEntry(check_window, width=180, height= 25)
        entry.pack(pady=5)
        ctk.CTkButton(check_window, text="habit finished", command=check_action,font=button_font, fg_color="royalblue").pack(pady=10)

    def show_all_habits_from_manager(self):
        # get the habits from the HabitManager
        habits_text = self.habit_manager.show_all_habits()
        self.update_display(habits_text)

    def show_habits(self,periodicity):
        """  displays the habits based on the selected periodicity  """
        message = self.habit_manager.show_habits_by_periodicity(periodicity)
        self.update_display(message)

    def analyze_habits(self):
           

        analysis_window = ctk.CTkToplevel(self.root)
        analysis_window.title("analyze your habits")
        analysis_window.geometry("400x300+750+570")

        # Keep the new window on top temporarily
        analysis_window.attributes("-topmost", True)
        analysis_window.after(100, lambda: analysis_window.attributes("-topmost", False))

        button_font = ("Arial", 14)
        
        #buttons for the different periodicites
        ctk.CTkButton(analysis_window, text="show all my habits", command = self.show_all_habits_from_manager,font=button_font, fg_color="royalblue").pack(pady=5)
        ctk.CTkButton(analysis_window, text="show all daily habits", command= lambda: self.show_habits(1),font=button_font, fg_color="royalblue").pack(pady=5)
        ctk.CTkButton(analysis_window, text="show all weekly habits", command=lambda: self.show_habits(7),font=button_font, fg_color="royalblue").pack(pady=5)
        ctk.CTkButton(analysis_window, text="show all monthly habits", command=lambda: self.show_habits(28),font=button_font, fg_color="royalblue").pack(pady=5)


        def display_most_misses():
            """ prints the habits that was missed to be checked off the most """
            result = self.habit_manager.most_misses()
            self.update_display(result)  

        button_font = ("Arial", 14)    

        #button for " what did I struggle with the most"
        ctk.CTkButton(analysis_window, text="What Habit Did I Struggle With the Most Last Month", command=display_most_misses,font=button_font, fg_color="royalblue").pack(pady=5)

        def display_longest_streak():
            """ prints the habit with the longest streak """
            result = self.habit_manager.longest_streak()
            if result is None:
                self.update_display("No habits found.")
            else:
                self.update_display(f"Your longest streak is {result['longest_streak']} for the habit '{result['name']}'.\n")

        button_font = ("Arial", 14)

        #button for longest streak
        ctk.CTkButton(analysis_window, text="show the habit with the longest streak", command = display_longest_streak,font=button_font, fg_color="royalblue").pack(pady=5)


        def open_streak_window():
            streak_window = ctk.CTkToplevel(analysis_window)
            streak_window.title("find longest streak")
            streak_window.geometry("400x300+750+570")

            # Keep the new window on top temporarily
            streak_window.attributes("-topmost", True)
            streak_window.after(100, lambda: streak_window.attributes("-topmost", False))

            # label for user instruction
            ctk.CTkLabel(streak_window, text="Enter the name of the habit you want to see your streak of").pack(pady=10)
            
            # opens the window for user input 
            entry = ctk.CTkEntry(streak_window,width=180, height= 25)
            entry.pack(pady=5)

            # button to find the streak
            def find_streak():
                habit_name = entry.get().strip()
                # ensure that the input is not empty
                if habit_name:
                    result = self.habit_manager.longest_streak_for_habit(habit_name)
                    self.update_display(result)
                    # close the window after button click
                    streak_window.destroy()
                else:
                    CTkMessagebox(title="Error - input required", message= "Please enter the name of the habit you want to see the longest streak of.")


            button_font = ("Arial", 14)
            ctk.CTkButton(streak_window, text="find streak", command= find_streak,font=button_font, fg_color="royalblue").pack(pady=10)

        ctk.CTkButton(analysis_window, text="show the longest streak for a specific habit", command=open_streak_window,font=button_font, fg_color="royalblue").pack(pady=5)



        

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitGUI(root)
    root.mainloop()



