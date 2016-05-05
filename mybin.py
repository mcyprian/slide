#!/usr/bin/python3

import sys
import argparse

from slide.entailment import main
from slide.performance_analyzer import check_performance, compare_results

parser = argparse.ArgumentParser()
parser.add_argument("--run",
                    required=False,
                    metavar='lhs rhs',
                    nargs=2,
                    help="input files containing definitions of lhs rhs.")
parser.add_argument("--performance-check",
                    required=False,
                    help="Run check of current slide performance."
                    )
parser.add_argument("--result-comparision",
                    required=False,
                    nargs=2,
                    help="Compare results of two previous checks."
                    )
args = parser.parse_args()

if args.performance_check:
    check_performance(sys.argv)
elif args.result_comparision:
    compare_results(sys.argv)
else:
    main(sys.argv[1:])
