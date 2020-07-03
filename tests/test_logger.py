from datetime import datetime
import os
import pathlib
import sqlite3
import unittest

import flowtime_logger.logger as logger


class TestTask(unittest.TestCase):

    def setUp(self):

        self.task = logger.Task('test')
        self.update_periods()

    def test_task_init(self):
        """Test the Task initialization."""
        self.assertIsInstance(self.task.start_time, datetime)
        self.assertEqual(self.task.start_time,
                         self.current_wp.wp_start_time)
        self.assertEqual(self.task.wp_count, 1)
        self.assertEqual(len(self.task.wp_list), 1)
        self.assertEqual(len(self.task.bp_list), 0)
        self.assertEqual(self.task.description, 'test')
        self.assertIsNone(self.task.end_time)
        self.assertIs(self.task.task_running, True)
        self.assertIs(self.task.task_ended, False)

    def test_task_stop(self):
        """Test the Task's stop() method when used correctly."""
        self.task.stop()
        self.update_periods()

        self.assertIsInstance(self.current_wp.wp_end_time, datetime)
        self.assertIsInstance(self.current_bp.bp_start_time, datetime)
        self.assertEqual(self.current_wp.wp_end_time,
                         self.current_bp.bp_start_time)
        self.assertEqual(len(self.task.wp_list), 1)
        self.assertEqual(len(self.task.bp_list), 1)
        self.assertIsNone(self.task.end_time)
        self.assertIs(self.task.task_running, False)
        self.assertIs(self.task.task_ended, False)

    def test_task_cont(self):
        """Test the Task's cont() method when used correctly."""
        self.task.stop()
        self.task.cont()
        self.update_periods()

        self.assertIsInstance(self.current_wp.wp_start_time, datetime)
        self.assertIsInstance(self.current_bp.bp_end_time, datetime)
        self.assertEqual(self.current_wp.wp_start_time,
                         self.current_bp.bp_end_time)
        self.assertEqual(len(self.task.wp_list), 2)
        self.assertEqual(len(self.task.bp_list), 1)
        self.assertIsNone(self.task.end_time)
        self.assertIs(self.task.task_running, True)
        self.assertIs(self.task.task_ended, False)

    def test_task_end(self):
        """Test the Task's end() method when used correctly."""
        self.task.stop()
        self.task.end()
        self.update_periods()

        self.assertEqual(len(self.task.wp_list), 1)
        self.assertEqual(len(self.task.bp_list), 0)
        self.assertEqual(self.task.end_time, self.current_wp.wp_end_time)
        self.assertIs(self.task.task_running, False)
        self.assertIs(self.task.task_ended, True)

    def test_task_stop_when_already_stopped(self):
        """Test the Task's stop() method when the Task is already stopped.
        AssertionError should be raised.
        """
        self.task.stop()

        with self.assertRaises(AssertionError):
            self.task.stop()

    def test_task_cont_when_already_running(self):
        """Test the Task's cont() method when the Task is already running.
        AssertionError should be raised.
        """
        with self.assertRaises(AssertionError):
            self.task.cont()

    def test_task_end_when_already_ended(self):
        """Test the Task's end() method when the Task has already been ended.
        AssertionError should be raised.
        """
        self.task.stop()
        self.task.end()

        with self.assertRaises(AssertionError):
            self.task.end()

    def test_task_end_when_not_stopped(self):
        """Test the Task's end() method when the Task hasn't been stopped.
        AssertionError should be raised.
        """
        with self.assertRaises(AssertionError):
            self.task.end()

    def update_periods(self):

        try:
            self.current_wp = self.task.wp_list[-1]
        except IndexError:
            pass

        try:
            self.current_bp = self.task.bp_list[-1]
        except IndexError:
            pass


class TestTaskSave(unittest.TestCase):

    def setUp(self):
        self.task = logger.Task('test')
        self.task.stop()
        self.task.cont()
        self.task.stop()
        self.task.end()
        self.task_tuple = (1, self.task.description, self.task.start_time,
                           self.task.end_time)

        self.task2 = logger.Task('test2')
        self.task2.stop()
        self.task2.cont()
        self.task2.stop()
        self.task2.end()
        self.task2_tuple = (2, self.task2.description, self.task2.start_time,
                            self.task2.end_time)

        self.task_period_list = []
        self.list_count = 1
        for wp in self.task.wp_list:
            self.task_period_list.append((self.list_count, 'wp',
                                         wp.wp_start_time, wp.wp_end_time, 1))
            self.list_count += 1

        for bp in self.task.bp_list:
            self.task_period_list.append((self.list_count, 'bp',
                                         bp.bp_start_time, bp.bp_end_time, 1))
            self.list_count += 1

        for wp in self.task2.wp_list:
            self.task_period_list.append((self.list_count, 'wp',
                                         wp.wp_start_time, wp.wp_end_time, 2))
            self.list_count += 1

        for bp in self.task2.bp_list:
            self.task_period_list.append((self.list_count, 'bp',
                                         bp.bp_start_time, bp.bp_end_time, 2))
            self.list_count += 1

        self.flogger_dir = pathlib.Path(logger.__file__).parent
        self.path_to_db = self.flogger_dir.joinpath(self.flogger_dir,
                                                    'test.db')

    def test_task_save(self):
        """Test Task's save() method."""
        self.task.save(database='test.db')
        self.task2.save(database='test.db')

        conn = sqlite3.connect(self.path_to_db,
                               detect_types=sqlite3.PARSE_DECLTYPES |
                               sqlite3.PARSE_COLNAMES)
        c = conn.cursor()
        with conn:
            c.execute("""SELECT * FROM Tasks""")
            task1 = c.fetchone()
            task2 = c.fetchone()

            c.execute("""SELECT * FROM Periods""")
            periods = c.fetchall()

        self.assertTupleEqual(self.task_tuple, task1)
        self.assertTupleEqual(self.task2_tuple, task2)
        self.assertListEqual(self.task_period_list, periods)

    def tearDown(self):
        os.remove(self.path_to_db)


if __name__ == "__main__":
    unittest.main()
