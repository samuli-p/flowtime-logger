"""
GUI for the Flowtime logger app

Classes
-------

FLoggerGUI
    A GUI for the logger part of the Flowtime logger app.

"""

import atexit
from tkinter import ttk


class FLoggerGUI():  # View
    """
    A GUI for the logger part of the Flowtime logger app.

    Methods
    -------

    - state1()
    - state2()
    - state3()
    - state4()

    For more information about the methods,
    check each method's individual docstring.

    """

    def __init__(self, parent, controller):
        """
        Create and place all the frames and widgets into root window.

        Widgets
        -------

        - root
            - main_frame
                - entry_frame
                    - td_label
                    - td_entry
                - time_frame
                    - start_label
                    - st_label
                    - end_label
                    - et_label
                - button_frame
                    - button1
                    - button2
                    - button3

        """

        self.parent = parent
        self.controller = controller
        # Create frames
        self.main_frame = ttk.Frame(self.parent, padding=6)
        self.main_frame.grid(column=0, row=0, sticky='nwes')
        self.entry_frame = ttk.Frame(self.main_frame)
        self.entry_frame.grid(column=0, row=0, sticky='nwe')
        self.time_frame = ttk.Frame(self.main_frame)
        self.time_frame.grid(column=0, row=1, sticky='we')
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(column=0, row=2, sticky='wes')

        # Set resizing magic for the frames
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1, uniform='b')
        self.main_frame.rowconfigure(1, weight=1, uniform='b')
        self.main_frame.rowconfigure(2, weight=1, uniform='b')
        self.entry_frame.columnconfigure(0, weight=1, uniform='a')
        self.entry_frame.columnconfigure(1, weight=1, uniform='a')
        self.time_frame.columnconfigure(0, weight=1, uniform='a')
        self.time_frame.columnconfigure(1, weight=1, uniform='a')
        self.button_frame.columnconfigure(0, weight=1, uniform='a')
        self.button_frame.columnconfigure(1, weight=1, uniform='a')

        # Create widgets inside the frames
        self.td_label = ttk.Label(self.entry_frame, text='Task description')
        self.td_entry = ttk.Entry(self.entry_frame)
        self.start_label = ttk.Label(self.time_frame, text='Start time:')
        self.end_label = ttk.Label(self.time_frame, text='End time:')
        self.st_label = ttk.Label(self.time_frame, text='0')
        self.et_label = ttk.Label(self.time_frame, text='0')
        self.button1 = ttk.Button(self.button_frame, text='Start', width=7,
                                  state='disabled')
        self.button2 = ttk.Button(self.button_frame, text='Stop', width=7,
                                  state='disabled')
        self.button3 = ttk.Button(self.button_frame, text='Quit', width=7,
                                  command=quit)

        # Place widgets
        self.td_label.grid(column=0, row=0, columnspan=2)
        self.td_entry.grid(column=0, row=1, columnspan=2, sticky='we')
        self.start_label.grid(column=0, row=0, sticky='e')
        self.end_label.grid(column=0, row=1, sticky='e')
        self.st_label.grid(column=1, row=0, sticky='w')
        self.et_label.grid(column=1, row=1, sticky='w')
        self.button1.grid(column=0, row=0, sticky='e')
        self.button2.grid(column=1, row=0, sticky='w')
        self.button3.grid(column=0, row=1, columnspan=2)

        # Set the minimum size of the window
        self.parent.update()
        window_width = self.parent.winfo_width()
        window_height = self.parent.winfo_height()
        self.parent.minsize(window_width, window_height)

        # Give focus to the Task description entry
        self.td_entry.focus()

        # Run check_entry function on KeyRelease event on the entry box
        self.td_entry.bind('<KeyRelease>', self.check_entry)

        # At program exit run controller.exit_app function
        atexit.register(self.controller.exit_handler)

    def check_entry(self, event):
        '''
        Checks the contents of the entry box.
        - Enables the Start button if td_entry is not empty.
        - Disables the Start button if td_entry is empty.
        '''

        if self.td_entry.get():
            self.button1.configure(text='Start', state='!disabled',
                                   command=self.controller.start_task)
        else:
            self.button1.state(['disabled'])

    def state1(self):
        """
        GUI state 1.

        Call this state after the 'New' button has been pressed.
        """

        self.button1.configure(text='Start', state='disabled',
                               command=self.controller.start_task)
        self.button2.configure(text='Stop', state='disabled',
                               command=self.controller.stop_task)
        self.td_entry.state(['!disabled'])
        self.td_entry.focus()
        self.td_entry.delete(0, 'end')
        self.st_label['text'] = '0'
        self.et_label['text'] = '0'

    def state2(self, start_time):
        """
        GUI state 2

        Call this state after the 'Start' button has been pressed.
        """

        self.td_entry.state(['disabled'])
        self.st_label['text'] = start_time
        self.button1.state(['disabled'])
        self.button2.configure(text='Stop', state='!disabled',
                               command=self.controller.stop_task)

    def state3(self):
        """
        GUI state 3

        Call this state after the 'Stop' button has been pressed.
        """

        self.button1.configure(text='Continue', state='!disabled',
                               command=self.controller.cont_task)
        self.button2.configure(text='End', command=self.controller.end_task)

    def state4(self, end_time):
        """
        GUI state 4

        Call this state after the 'End' button has been pressed.
        """

        self.et_label['text'] = end_time
        self.button1.configure(text='New', command=self.controller.new_task)
        self.button2.state(['disabled'])
