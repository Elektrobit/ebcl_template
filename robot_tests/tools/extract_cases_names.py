#!/usr/bin/env python3
# extract_robot_tests.py
import sys
from robot.api import TestSuiteBuilder
from robot.errors import DataError

def get_test_names(robot_file_path):
    try:
        suite = TestSuiteBuilder().build(robot_file_path)
    except DataError:
        return ''
    test_cases = [test.name for test in suite.tests]
    return test_cases

if __name__ == "__main__":
    robot_file = sys.argv[1]
    test_cases = get_test_names(robot_file)
    print('["' + '","'.join(test_cases) + '"]')
