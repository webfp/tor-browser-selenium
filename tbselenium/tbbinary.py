from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class TBBinary(FirefoxBinary):
    '''
    Extend FirefoxBinary to better handle terminated browser processes.
    '''

    def kill(self):
        """Kill the browser.

        This is useful when the browser is stuck.
        """
        if self.process and self.process.poll() is None:
            self.process.kill()
            self.process.wait()
