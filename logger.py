"""
Create objects that represent tasks being performed and log them.

Classes:
--------

Task
    A class to represent a task being performed.

How to use this module:
-----------------------

Example of usage::

    import logger

    task = logger.Task('This is the description of the task')
    task.stop()
    task.cont()
    task.stop()
    task.end()
    task.save()

"""

from datetime import datetime
import csv


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
    starttime : datetime object
        Start time of the task.
    endtime : datetime object
        End time of the task.
    totaltime : datetime object
        Total time of the task including work and break periods.
    workingtime : datetime object
        Total working time of the task consisting of work periods.
    restingtime : datetime object
        Total resting time of the task consisting of break periods.
    wplist : list
        A list containing work period objects.
    bplist : list
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

        self.starttime = datetime.now()
        self.wplist = [WorkPeriod()]
        self.description = description
        self.endtime = None
        self.totaltime = None
        self.workingtime = None
        self.restingtime = None
        self.bplist = []
        self.task_dict = {}
        self.wpbp_dict = {}
        self.task_running = True
        self.task_ended = False

    def stop(self):
        """
        Stop the current work period, start a new break period and
        calculate the new working time.

        Should be called only when the task is running
        i.e. task_running = True and task_ended = False.
        """

        self.task_running = False
        self.wplist[-1].stop_wp()
        self.bplist.append(BreakPeriod())
        if self.workingtime is None:
            self.workingtime = self.wplist[-1].wplength
        else:
            self.workingtime += self.wplist[-1].wplength

    def cont(self):
        """
        Stop the current break period, start a new work period and
        calculate the new resting time.

        Should be called only when the task is stopped but not ended
        i.e. when task_running = False and task_ended = False.
        """

        self.task_running = True
        self.bplist[-1].stop_bp()
        self.wplist.append(WorkPeriod())
        if self.restingtime is None:
            self.restingtime = self.bplist[-1].bplength
        else:
            self.restingtime += self.bplist[-1].bplength

    def end(self):
        """
        End the task.

        Should be called only when the task is stopped but not ended
        i.e. when task_running = False and task_ended = False.
        """

        self.task_running = False
        self.task_ended = True
        # Set the task endtime to be the same as the stop time of the last
        # working period
        self.endtime = self.wplist[-1].wpstop

        # Remove the last item in the bplist since we're endin the task and
        # not taking another break
        self.bplist.pop()

        # Calculate the totaltime
        self.totaltime = self.endtime - self.starttime

        # Call the create_dict method
        self.create_dict()

    def create_dict(self):
        """
        Create two dictionaries called task_dict and wpbp_dict containing
        the data from Task, WorkPeriod and BreakPeriod.

        Called automatically by the end() method.
        """

        # Collect the data from Task to task_dict
        self.task_dict = {
            'Description': self.description,
            'Start time': self.starttime,
            'End time': self.endtime,
            'Total time': self.totaltime,
            'Working time': self.workingtime,
            'Resting time': self.restingtime,
            'Working periods': len(self.wplist),
            'Resting periods': len(self.bplist)
        }

        # Collect the data from WorkPeriod to wpbp_dict
        list_count = 0
        for wp in self.wplist:
            list_count += 1
            self.wpbp_dict['Work period '
                           + str(list_count)
                           + ' start'] = wp.wpstart
            self.wpbp_dict['Work period '
                           + str(list_count)
                           + ' stop'] = wp.wpstop
            self.wpbp_dict['Work period '
                           + str(list_count)
                           + ' length'] = wp.wplength

        # Collect the data form BreakPeriod to wpbp_dict
        list_count = 0
        for bp in self.bplist:
            list_count += 1
            self.wpbp_dict['Break period '
                           + str(list_count)
                           + ' start'] = bp.bpstart
            self.wpbp_dict['Break period '
                           + str(list_count)
                           + ' stop'] = bp.bpstop
            self.wpbp_dict['Break period '
                           + str(list_count)
                           + ' length'] = bp.bplength

    def save(self):
        """
        Save the data from the task_dict to a file called tasks.csv and
        create a separate file containing all the work period and break
        period data from the wpbp_dict.

        Should be called only when the task is stopped and ended
        i.e. when task_running = False and task_ended = True.
        """

        # Save the contents of task_dict to a file called tasks.csv
        with open('tasks.csv', mode='a') as csv_file:
            fieldnames = self.task_dict.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            # Write headers if the file is empty
            if csv_file.tell() == 0:
                writer.writeheader()
                writer.writerow(self.task_dict)
            # Else write only the data
            else:
                writer.writerow(self.task_dict)

        # Save the contents of wpbp_dict to a csv file using the task start
        # time as a filename
        filename = str(self.starttime) + '.csv'
        with open(filename, mode='w') as csv_file:
            fieldnames = self.wpbp_dict.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow(self.wpbp_dict)


class WorkPeriod:

    """
    A class to represent a work period in a task.

    Instance variables
    ------------------

    wpstart : datetime object
        Start time of the work period.
    wpstop : datetime object
        End time of the work period.
    wplength : datetime object
        Length of the work period.

    """

    def __init__(self):
        # Work period start and stop times and length
        self.wpstart = datetime.now()
        self.wpstop = None
        self.wplength = None

    def stop_wp(self):
        self.wpstop = datetime.now()
        self.wplength = self.wpstop - self.wpstart


class BreakPeriod:

    """
    A class to represent a break period in a task.

    Instance variables
    ------------------

    bpstart : datetime object
        Start time of the break period.
    bpstop : datetime object
        End time of the break period.
    bplength : datetime object
        Length of the break period.

    """

    def __init__(self):
        """
        Start a break period and construct all the instance variables.

        Set bpstart to current time
        """

        # Break period start, stop and length
        self.bpstart = datetime.now()
        self.bpstop = 0
        self.bplength = 0

    def stop_bp(self):
        self.bpstop = datetime.now()
        self.bplength = self.bpstop - self.bpstart
