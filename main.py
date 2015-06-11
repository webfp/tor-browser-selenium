import argparse
import traceback
import logging
import common as cm
import sys
from log import wl_log
import utils as ut
from datacollection.crawler import Crawler
#######################################
from selenium import tbbdriver
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