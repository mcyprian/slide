#!/usr/bin/python

# Michal Cyprian
# 
# analysis of slide performance
# distrubuted under GNU GPL licence

import sys
import os
import yaml
import pprint

import entailment


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


class PerformanceAnalyzer(object):
    """Analyzes performance of slide on given set of input files,
    creates dictionary of input files and results. Can store dictionary
    to yaml file or compare results of two analyses.
    """
    def __init__(self, input_dir, output_file=None):
        if not output_file:
            output_file = input_dir + "_analysis"

        self.input_dir = input_dir if input_dir[-1] == '/' else input_dir + '/'
        self.output_file = output_file
        self.input_files = sorted(os.listdir(input_dir))
        self.results = {}

    def analyse(self):
        output_stream = StringWriter()
        for _ in range(len(self.input_files) / 2):
            file_lhs, file_rhs = [self.input_dir + file_name for file_name in self.input_files[:2]]
            self.input_files = self.input_files[2:]
            try:
                entailment.main(file_lhs, file_rhs, verbose=False, enabled=True, output_stream=output_stream)
            except Exception as e:
                print("Exception occured")
                self.results[file_lhs[:-4]] = (e.__class__.__name__, e.message)
            else:
                self.results[file_lhs[:-4]] = output_stream.content
            output_stream.empty()
            print("file: {0} result: {1}".format(file_lhs[:-4], output_stream.content))
        pprint.pprint(self.results)
        pprint.pprint(self.statistics)
        self.save_output()

    @property
    def statistics(self):
        stat_dict = invert_dict(self.results)
        for key in stat_dict.keys():
            stat_dict[key] = len(stat_dict[key])
        return stat_dict

    @property
    def yaml_statistics(self):
        return yaml.dump(self.statistics)

    @property
    def yaml_results(self):
        return yaml.dump(self.results)

    def save_output(self):
        with open(self.output_file, 'w') as fo:
            fo.write(self.yaml_results)
            fo.write(self.yaml_statistics)


def invert_dict(input_dict):
    """Returns dictionary with inverted keys, values.
    inputdict {1 : 'a', 2 : 'b', 3 : 'a'} -> {'a' : [1, 3], 'b' : [2]}
    """
    inverted_dict = {}
    for key, value in input_dict.items():
        inverted_dict[value] = inverted_dict.get(value, [])
        inverted_dict[value].append(key)
    return inverted_dict


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write("Invalid command line arguments, usage: ./performance_analyzer.py TEST_DIR\n")
        sys.exit(1)

    perform_analyzer = PerformanceAnalyzer(sys.argv[1])
    perform_analyzer.analyse()
