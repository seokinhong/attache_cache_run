#!/bin/python
import os
import sys

id=sys.argv[1]
cmd = "./show.py -c l3 -t misses -i %s"%id
print cmd
os.system(cmd)
