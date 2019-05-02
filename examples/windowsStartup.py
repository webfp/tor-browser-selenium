from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.options import Log
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

binary = "Tor Browser/Browser/firefox.exe"
profile = "Tor Browser/Browser/TorBrowser/Data/Browser/profile.default"
self.driver = TorBrowserDriver(tbb_fx_binary_path=binary, tbb_profile_path=profile, service_log_path="Logs/geckodriver.log")     #start selenium
