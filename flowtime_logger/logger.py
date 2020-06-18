"""
Create objects that represent tasks being performed and log them.

Classes:
--------

Task
    A class to represent a task being performed.

"""

import pathlib
import sqlite3
from datetime import datetime


class Task:

    """
    A class to represent a task being performed.

    Parameters
    ----------

    description : string
        A description of the task

    Methods
    -------

    stop()
        Stop the task.
    cont()
        Continue the task.
    end()
        End the task.
    save()
        Save the task.

    Instance variables
    ------------------

    description : str
        Description of the task.
    start_time : datetime object
        Start time of the task.
    end_time : datetime object
        End time of the task.
    wp_list : list
        A list containing work period objects.
    bp_list : list
        A list containing break period objects.
    task_running : boolean
        Indicates whether the task is running or not.

        Also can be used together with the task_ended boolean to determine
        whether the task is stopped or not.
    task_ended : boolean
        Indicates whether the task has been ended or not.

        Also can be used together with the task_running boolean to determine
        whether the task is stopped or not.

    """

    def __init__(self, description):
        """
        Start a task and the first work period of the task.
        Construct all the instance variables for the task object.

        Parameters
        ----------

        description : string
            A description of the task

        """

        self.start_time = datetime.now()
        self.wp_count = 0
        self.wp_list = [WorkPeriod(self)]
        self.description = description
        self.end_time = None
        self.bp_list = []
        self.task_running = True
        self.task_ended = False

    def stop(self):
        """
        Stop the current work period and start a new break period.

        Should be called only when the task is running
        i.e. task_running = True and task_ended = False.
        """
        assert self.task_running, 'Can\'t stop a Task that is not running.'
        self.task_running = False
        self.wp_list[-1].end_wp()
        self.bp_list.append(BreakPeriod(self))

    def cont(self):
        """
        Stop the current break period and start a new work period.

        Should be called only when the task is stopped but not ended
        i.e. when task_running = False and task_ended = False.
        """

        assert not self.task_running, 'Can\'t continue a Task that is already\
 running.'
        self.task_running = True
        self.bp_list[-1].end_bp()
        self.wp_list.append(WorkPeriod(self))

    def end(self):
        """
        End the task.

        Should be called only when the task is stopped but not ended
        i.e. when task_running = False and task_ended = False.
        """

        assert not self.task_ended, 'Can\'t end a Task that has already been\
 ended'
        assert not self.task_running, 'The Task needs to be stopped before it\
 can be ended.'
        self.task_running = False
        self.task_ended = True
        # Set the task end_time to be the same as the stop time of the
        # last working period
        self.end_time = self.wp_list[-1].wp_end_time
        # Remove the last item in the bp_list since we're endin the
        # task and not taking another break
        self.bp_list.pop()

    def save(self, database='flogger.db'):
        """
        Save the Task, WorkPeriod and BreakPeriod data into a SQLite database.

        The default filename for the database is: flogger.db

        Tables:
        -------

        Tasks
            id, description, start_time, end_time
        Periods
            id, type, start_time, end_time, task_id

        """

        flogger_dir = pathlib.Path(__file__).parent
        path_to_db = flogger_dir.joinpath(flogger_dir, database)

        conn = sqlite3.connect(path_to_db,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                               sqlite3.PARSE_COLNAMES)
        c = conn.cursor()

        # Create tables
        try:  # Raises an OperationalError if the table already exists.
            with conn:
                c.execute("""CREATE TABLE Tasks (
                             id INTEGER PRIMARY KEY,
                             description TEXT,
                             start_time timestamp,
                             end_time timestamp
                         )""")
        except sqlite3.OperationalError:
            pass

        try:  # Raises an OperationalError if the table already exists.
            with conn:
                c.execute("""CREATE TABLE Periods (
                             id INTEGER PRIMARY KEY,
                             type TEXT,
                             start_time timestamp,
                             end_time timestamp,
                             task_id INTEGER
                         )""")
        except sqlite3.OperationalError:
            pass

        with conn:
            # Insert task into database.
            c.execute("""INSERT INTO Tasks (description, start_time, end_time)
                         VALUES (:description, :start, :end)""",
                      {'description': self.description,
                       'start': self.start_time,
                       'end': self.end_time})

            # Fetch the task id from database...
            c.execute("""SELECT id FROM Tasks WHERE
                         start_time = :start""",
                      {'start': self.start_time})

            # ...and assign it to a task_id variable.
            task_id = c.fetchone()[0]

            # Insert work periods into database.
            for wp in self.wp_list:
                c.execute("""INSERT INTO Periods (type, start_time, end_time,
                             task_id) VALUES (:type, :start, :end, :task)""",
                          {'type': 'wp',
                           'start': wp.wp_start_time,
                           'end': wp.wp_end_time,
                           'task': task_id})

            # Insert break periods into database.
            for bp in self.bp_list:
                c.execute("""INSERT INTO Periods (type, start_time, end_time,
                             task_id) VALUES (:type, :start, :end, :task)""",
                          {'type': 'bp',
                           'start': bp.bp_start_time,
                           'end': bp.bp_end_time,
                           'task': task_id})


class WorkPeriod:

    """
    A class to represent a work period in a task.

    Instance variables
    ------------------

    wp_start_time : datetime object
        Start time of the work period.
    wp_end_time : datetime object
        End time of the work period.

    """

    def __init__(self, master):
        """Set the work period start time and construct variables"""

        self.master = master
        if self.master.wp_count > 0:
            self.wp_start_time = self.master.bp_list[-1].bp_end_time
        else:
            self.wp_start_time = self.master.start_time
        self.master.wp_count += 1
        self.wp_end_time = None

    def end_wp(self):
        self.wp_end_time = datetime.now()


class BreakPeriod:

    """
    A class to represent a break period in a task.

    Instance variables
    ------------------

    bp_start_time : datetime object
        Start time of the break period.
    bp_end_time : datetime object
        End time of the break period.

    """

    def __init__(self, master):
        """
        Set the break period start time and construct all the instance
        variables.
        """

        self.master = master
        self.bp_start_time = self.master.wp_list[-1].wp_end_time
        self.bp_end_time = None

    def end_bp(self):
        """Set the break period end time"""

        self.bp_end_time = datetime.now()
