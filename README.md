# Habit Tracking Application
This application lets users create habits, monitor their progress, helps them to stay motivated and keep track of what habits they still need to work on.

## Functionality of the application
* The application lets the user add habits with a specific name & periodicity.  
* The user can choose between daily, weekly, monthly or custom periodicities, like every 2 / 3 / 5 / ... days.  
* The user can delete habits by entering the respective habit name inside an entry window.  
* The user can check off each habit by entering the respective habit name inside an entry window.  
* The user can display all habits, sort them by periodicity and analyze them to figure out what the user is doing good and what he / she is struggling with.  

This project is build with Python and stores the habit data in a SQLite3 database as well as an in-memory dictionary.  

It comes with a graphical user interface to ensure an intuitive user experience.  



## Which requirements are necessary for installation ? 
For the GUI as well as the pytests it is required to install multiple dependencies.  

Follow these steps to install the project :  

1. clone the repository to your local machine:  

2. create a virtual environment by entering  
    " py -m venv .virtual_environment " in the terminal  

3. activate the venv by entering  
    " source .virtual_environment/Scripts/activate "     
    " source virtual_environment/bin/activate " on Linux / apple systems  

4. enter " pip install -r requirements.txt " in the terminal to install all the necessary dependencies  

## Usage of the application

1. run the " main.py " -> the GUI will open an you can click the buttons for the desired action  
2. follow the instructions in the entry windows that open automatically.  
3. in case of wrong inputs pay attention to the error messages that pop up, they tell you what caused the error and what input is needed.  

## Testing the code

You run the tests by entering " pytest -v " in the terminal, this runs every test function.  

If you only want to test a specific file enter " pytest filename ".  
Example:  
pytest test_habits.py  
pytest test_HabitManager.py  
pytest test_main.py  

