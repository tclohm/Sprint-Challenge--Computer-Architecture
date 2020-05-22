#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

try:
 	file = sys.argv[1]
 	cpu = CPU()
 	cpu.load(file)
 	cpu.run()
except:
	print("🏃‍♀️📄 \033[91m" + "Please run with a file" + "\033[0m")