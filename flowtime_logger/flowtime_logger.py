"""
This is the main controller module for the Flowtime logger application.

Classes
-------

MainApp
    The controller class for the whole app.

"""

import sys
import tkinter as tk

from floggergui import FLoggerGUI
import logger


class MainApp:  # Controller
    """
    The controller class for the whole app.

    Methods:
    --------

    - start_task()
    - stop_task()
    - cont_task()
    - end_task()
    - new_task()
    - exit_handler()

    For more information about the methods,
    check each method's individual docstring.
    """

    def __init__(self):
        """
        Initialize the app.

        - Create the root window.
        - Load the logger GUI
        - Start the mainloop

        """

        self.root = tk.Tk()
        self.root.title("Flowtime logger")
        self.gui = FLoggerGUI(self.root, self)
        self.root.mainloop()

    def start_task(self):
        """Start the task."""

        self.description = self.gui.td_entry.get()
        self.task = logger.Task(self.description)
        self.gui.state2(self.task.start_time.strftime('%X'))

    def stop_task(self):
        """Stop the task."""

        self.task.stop()
        self.gui.state3()

    def cont_task(self):
        """Continue the task."""

        self.task.cont()
        self.gui.state2(self.task.start_time.strftime('%X'))

    def end_task(self):
        """End and save the task into database."""

        self.task.end()
        self.task.save()
        self.gui.state4(self.task.end_time.strftime('%X'))

    def new_task(self):
        """Create a new task."""

        self.gui.state1()

    def exit_handler(self):
        '''
        Stops and ends the task if it's running before exiting the program.
        '''

        try:  # Raises an AttributeError if no task was started.
            if self.task.task_running:
                self.task.stop()
            if not self.task.task_ended:
                self.task.end()
                self.task.save()
        except AttributeError:
            pass
        sys.exit()


if __name__ == "__main__":
    main = MainApp()
