import pytest
from unittest import mock
from unittest.mock import MagicMock, patch
from habit_manager import HabitManager
from main import scheduled_reset

@pytest.fixture
def habit_manager():
    """ fixture that creates a mock HabitManager """
    mock_manager = MagicMock(spec = HabitManager)
    mock_manager.habits = {
        "habit1" : MagicMock(),
        "habit2" : MagicMock()
    }
    return mock_manager

def test_scheduled_reset(habit_manager):
    """ testing if scheduled_reset calls reset_checked_off for all the habits """

    # call the method
    scheduled_reset(habit_manager)

    # check if reset_checked_off was called for each habit
    for habit in habit_manager.habits.values():
        habit.reset_checked_off.assert_called_once()

@patch("main.BackgroundScheduler")
def test_scheduler_starts(self):
    """ testing if the scheduler starts correctly """

    # create a HabitManager instance
    habit_manager = HabitManager("habit.db")

    # create a scheduler mock
    scheduler = mock.Mock()

    # run the code
    scheduler.add_job(scheduled_reset, 'cron', hour = 23, minute = 59, second = 57, args =[habit_manager])

    # assert that the the add_job method was called with the expected arguments
    scheduler.add_job.assert_called_once_with(
        scheduled_reset,
        'cron',
        hour = 23,
        minute = 59,
        second = 57,
        args=[habit_manager]
    )
