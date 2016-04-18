#!/usr/bin/python3

"""Michal Cyprian

Analysis of slide performance
distrubuted under GNU GPL licence
"""

import sys
import os
import yaml
import pprint
import datetime
from abc import ABCMeta

from slide import entailment


class StringWriter(object):
    """Class to redirect file descriptor (stdout) to string variable."""

    def __init__(self):
        self.content = ''

    def write(self, message):
        self.content += message.rstrip('\n')

    def read(self):
        return self.content

    def flush(self):
        pass

    def empty(self):
        self.content = ''


class PerformanceObject(metaclass=ABCMeta):
    """Abstract base class of performance comparing classes"""

    def __init__(self, output_file=None):
        if not output_file:
            date = datetime.date.today()
            output_file = date.__str__()
        self.output_file = output_file

    def yaml_attr(self, attr):
        return yaml.dump(getattr(self, attr))

    def save_output(self, attr):
        with open(self.output_file + '_' + attr, 'w') as fo:
            fo.write(self.yaml_attr(attr))

    def load_file(self, file_name):
        with open(file_name, 'r') as fi:
            return fi.read()


class PerformanceAnalyzer(PerformanceObject):
    """Analyzes performance of slide on given set of input files,
    creates dictionary of input files and results. Can store dictionary
    to yaml file or compare results of two analyses.
    """

    def __init__(self, input_dir, output_file=None):
        super(PerformanceAnalyzer, self).__init__(output_file)

        self.input_dir = input_dir if input_dir[-1] == '/' else input_dir + '/'
        self.input_files = sorted(os.listdir(input_dir))
        self.results = {}

    def analyse(self):
        output_stream = StringWriter()
        for _ in range(len(self.input_files) // 2):
            file_lhs, file_rhs = [self.input_dir + file_name for file_name in self.input_files[:2]]
            file_name = file_lhs.split('/')[-1][:-4]
            self.input_files = self.input_files[2:]
            try:
                entailment.entailment(
                    file_lhs,
                    file_rhs,
                    verbose=False,
                    enabled=True,
                    output_stream=output_stream)
            except Exception as e:
                self.results[file_name] = (e.__class__.__name__, e.args)
            else:
                self.results[file_name] = output_stream.content
            output_stream.empty()
        pprint.pprint(self.results)
        pprint.pprint(self.statistics)
        self.save_output('results')
        self.save_output('statistics')

    @property
    def statistics(self):
        stat_dict = invert_dict(self.results)
        for key in stat_dict.keys():
            stat_dict[key] = len(stat_dict[key])
        return stat_dict


class PerformanceComparer(PerformanceObject):
    """Compares results from two yaml files containig
    PerformanceAnalyzer output."""

    def __init__(self, first, second, output_file=None):
        super(PerformanceComparer, self).__init__(output_file)
        self.first = yaml.load(self.load_file(first))
        self.second = yaml.load(self.load_file(second))
        self.acceptable_change = {}
        self.unacceptable_change = {}

    def compare(self):
        for key in self.first.keys():
            if self.first[key] != self.second[key]:
                first_key = self.first[key]
                second_key = self.second[key]
                if ((isinstance(first_key, tuple) and isinstance(second_key, tuple)) or
                        (first_key == 'UNKNOWN') or
                        (first_key == 'INVALID' and isinstance(second_key, tuple)) or
                        (second_key == 'INVALID' and isinstance(first_key, tuple))):
                    self.acceptable_change[key] = (first_key, second_key)
                else:
                    self.unacceptable_change[key] = (first_key, second_key)

        pprint.pprint(self.acceptable_change)
        pprint.pprint(self.unacceptable_change)
        self.save_output('acceptable_change')
        self.save_output('unacceptable_change')


def invert_dict(input_dict):
    """Returns dictionary with inverted keys, values.
    inputdict {1 : 'a', 2 : 'b', 3 : 'a'} -> {'a' : [1, 3], 'b' : [2]}
    """
    inverted_dict = {}
    for key, value in input_dict.items():
        inverted_dict[value] = inverted_dict.get(value, [])
        inverted_dict[value].append(key)
    return inverted_dict


def check_performance(sys_argv):
    if len(sys_argv) < 3:
        sys.stderr.write(
            "Invalid command line arguments, usage: ./performance_analyzer.py TEST_DIR\n")
        sys.exit(1)

    if sys_argv[2] == "-c":
        if len(sys.argv) < 5:
            sys.stderr.write(
                "Invalid command line arguments, usage: ./performance_analyzer.py TEST_DIR\n")
            sys.exit(1)
        else:
            perform_comparer = PerformanceComparer(*sys_argv[3:])
            perform_comparer.compare()
            sys.exit(0)

    perform_analyzer = PerformanceAnalyzer(*sys_argv[2:])
    perform_analyzer.analyse()
