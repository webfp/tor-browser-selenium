#!/usr/bin/python
from argparse import ArgumentParser
from subprocess import call
from os import environ
from os.path import isdir, realpath, dirname, join


desc = "Run all the TorBrowserDriver tests"
parser = ArgumentParser(description=desc)
parser.add_argument('tbb_path')
args = parser.parse_args()

if not isdir(args.tbb_path):
    raise IOError("Please pass the path to Tor Browser Bundle")

# TBB_PATH environment variable is used by the tests
environ['TBB_PATH'] = args.tbb_path

# Get test directory from path of this script
file_path = dirname(realpath(__file__))
test_dir = join(file_path, 'tbselenium', 'test')

# Run all the tests using py.test
call(["py.test", "-s", "-v", "--cov=tbselenium", "--cov-report",
      "term-missing", "--durations=10", test_dir])
