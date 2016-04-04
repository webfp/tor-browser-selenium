#!/usr/bin/python
import sys
from subprocess import call
from os import environ
from os.path import isdir, realpath, dirname, join

# Validate input
if len(sys.argv) != 2:
    print "ERROR: the path to the Tor Browser Bundle directory is a required argument."
    sys.exit(-1)

if sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print "This script runs all the tests of the tor-browser-selenium project.\n" \
          "It requires as argument the path to a Tor Browser Bundle directory."
    sys.exit(0)

tbb_path = sys.argv[1]
if not isdir(tbb_path):
    print "ERROR: the argument does not point to a directory."
    sys.exit(-1)
environ['TBB_PATH'] = tbb_path

# Get test directory from path of this script
file_path = dirname(realpath(__file__))
test_dir = join(file_path, 'tbselenium', 'test')

# Run all tests
call(["python", "-m", "unittest", "discover", test_dir])
