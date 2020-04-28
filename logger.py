from datetime import datetime
import csv

class WorkPeriod:
    
    def __init__(self):
        # Work period start and stop times and length
        self.wpstart = datetime.now()
        self.wpstop = None
        self.wplength = None
    
    def stop_wp(self):
        self.wpstop = datetime.now()
        self.wplength = self.wpstop - self.wpstart

class BreakPeriod:
    def __init__(self):
        # Break period start, stop and length
        self.bpstart = datetime.now()
        self.bpstop = 0
        self.bplength = 0
    
    def stop_bp(self):
        self.bpstop = datetime.now()
        self.bplength = self.bpstop - self.bpstart
        

class Task:

    def __init__(self, description):
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
    
    def stop(self):
        '''Stops the current work period, starts a new break period and
        calculates the new working time
        '''
        
        self.wplist[-1].stop_wp()
        self.bplist.append(BreakPeriod())
        if self.workingtime is None:
            self.workingtime = self.wplist[-1].wplength
        else:
            self.workingtime += self.wplist[-1].wplength

    def cont(self):
        '''Stops the current break period, starts a new work period and
        calculates the new resting time
        '''

        self.bplist[-1].stop_bp()
        self.wplist.append(WorkPeriod())
        if self.restingtime is None:
            self.restingtime = self.bplist[-1].bplength
        else:
            self.restingtime += self.bplist[-1].bplength
    
    def end(self):
        '''Ends the task
        '''
        # Set the task endtime to be the same as the stop time of the last working period
        self.endtime = self.wplist[-1].wpstop
        
        # Remove the last item in the bplist since we're endin the task and not taking another break
        self.bplist.pop()

        # Calculate the totaltime
        self.totaltime = self.endtime - self.starttime

        # Call the create_dict method
        self.create_dict()
    
    def create_dict(self):
        '''Creates two dictionaries called task_dict and wpbp_dict containing the data from 
        Task, WorkPeriod and BreakPeriod
        '''
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
            self.wpbp_dict['Work period ' + str(list_count) + ' start'] = wp.wpstart
            self.wpbp_dict['Work period ' + str(list_count) + ' stop'] = wp.wpstop
            self.wpbp_dict['Work period ' + str(list_count) + ' length'] = wp.wplength
        
        # Collect the data form BreakPeriod to wpbp_dict
        list_count = 0
        for bp in self.bplist:
            list_count += 1
            self.wpbp_dict['Break period ' + str(list_count) + ' start'] = bp.bpstart
            self.wpbp_dict['Break period ' + str(list_count) + ' stop'] = bp.bpstop
            self.wpbp_dict['Break period ' + str(list_count) + ' length'] = bp.bplength
    
    def save(self):
        '''Saves the data from the task_dict to a file called tasks.csv and creates a separate file
        containing all the work period and break period data from the wpbp_dict.
        '''
        # One could use the pandas library for this bit but I stuck with the csv from the standard library

        # Save the contents of task_dict to a file called tasks.csv        
        with open ('tasks.csv', mode='a') as csv_file:
            fieldnames = self.task_dict.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            if csv_file.tell() == 0:                # Write headers if the file is empty
                writer.writeheader()
                writer.writerow(self.task_dict)
            else:
                writer.writerow(self.task_dict)     # Otherwise write only the data
        
        # Save the contents of wpbp_dict to a csv file using the task start time as a filename
        filename = str(self.starttime) + '.csv'
        with open (filename, mode='w') as csv_file:
            fieldnames = self.wpbp_dict.keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow(self.wpbp_dict)