#!/usr/bin/python3

import sys
import argparse

from slide.entailment import main
from slide.performance_analyzer import check_performance

parser = argparse.ArgumentParser()
parser.add_argument("--run",
                    required=False,
                    metavar='lhs rhs',
                    nargs=2,
                    help="input files containing definitions of lhs rhs.")
parser.add_argument("--performance-check",
                    required=False,
                    help="Run check of currnet slide performance."
                    )
args = parser.parse_args()

if args.performance_check:
    check_performance(sys.argv)
else:
    main(sys.argv[1:])
