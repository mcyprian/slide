#!/usr/bin/python3

import sys
from slide.entailment import main
from slide.performance_analyzer import check_performance

if len(sys.argv) > 1 and sys.argv[1] == "--performance_check":
    check_performance(sys.argv)
else:
    main(sys.argv)
