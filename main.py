import argparse
import traceback
import logging
import common as cm
import sys
from log import wl_log
import utils as ut
from datacollection.crawler import Crawler
#######################################
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#######################################

def get_by_tor_sel():
    driver = webdriver.Firefox()
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element_by_name("q")
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
    driver.close()

if __name__ == '__main__':
    get_by_tor_sel()
    
       
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument('-x', '--xvfb', help='Use XVFB (for headless testing)',
                        action='store_true', default=False)
    parser.add_argument('-c', '--capture-screen',
                        help='Capture page screenshots',
                        action='store_true', default=False)
    args = parser.parse_args()
    verbose = args.verbose
    tbb_version = args.browser_version
    xvfb = args.xvfb
    capture_screen = args.capture_screen
    if verbose:
        wl_log.setLevel(logging.DEBUG)
    else:
        wl_log.setLevel(logging.INFO)

    if not tbb_version:
        # Assign the last stable version of TBB
        tbb_version = cm.TBB_DEFAULT_VERSION
    elif tbb_version not in cm.TBB_KNOWN_VERSIONS:
        ut.die("Version of Tor browser is not recognized."
               " Use --help to see which are the accepted values.")

    crawler = Crawler(torrc_dict, url_list, tbb_version,
                      experiment, xvfb, capture_screen)
    wl_log.info("Command line parameters: %s" % sys.argv)
