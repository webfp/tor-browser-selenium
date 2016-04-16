import signal
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.exceptions import TimeExceededError
from selenium.common.exceptions import (TimeoutException, WebDriverException)
from selenium.webdriver.common.utils import is_connectable

try:
    from httplib import CannotSendRequest
except ImportError:
    from http.client import CannotSendRequest
try:
    from stem.process import launch_tor_with_config
except ImportError as err:
    pass

MAX_FIXTURE_TRIES = 3
EXTERNAL_TIMEOUT_GRACE = 5  # only fire if the internal timeout fails
LAUNCH_TOR_TIMEOUT = 30 + EXTERNAL_TIMEOUT_GRACE
LOAD_PAGE_TIMEOUT = 60
TB_INIT_EXT_TIMEOUT = cm.TB_INIT_TIMEOUT + EXTERNAL_TIMEOUT_GRACE


class TorBrowserDriverFixture(TorBrowserDriver):
    """Extend TorBrowserDriver to have fixtures for tests."""
    def __init__(self, *args, **kwargs):
        last_err = RuntimeError("Unknown error")
        self.change_default_tor_cfg(kwargs)
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                timeout(TB_INIT_EXT_TIMEOUT)
                return super(TorBrowserDriverFixture, self).__init__(*args,
                                                                     **kwargs)
            except (TimeoutException, WebDriverException,
                    TimeExceededError) as last_err:
                print ("\nTBDriver init timed out. Attempt %s %s" %
                       ((tries + 1), last_err))
                super(TorBrowserDriverFixture, self).quit()  # clean up
                continue
            finally:
                cancel_timeout()
        else:
            raise last_err

    def change_default_tor_cfg(self, kwargs):
        """Use system Tor if the caller doesn't specifically wants
        to launch a new TBB Tor.

        This makes tests faster and more robust against network
        issues since otherwise we'd have to launch a new Tor process
        for each test.
        """

        if kwargs.get("tor_cfg") != cm.LAUNCH_NEW_TBB_TOR and\
                is_connectable(cm.DEFAULT_SOCKS_PORT):
            kwargs["tor_cfg"] = cm.USE_RUNNING_TOR
            # print ("Will use system Tor for the test")

    def load_url_ensure(self, *args, **kwargs):
        """Make sure the requested URL is loaded. Retry if necessary."""
        last_err = RuntimeError("Unknown error")
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                timeout(LOAD_PAGE_TIMEOUT)
                self.load_url(*args, **kwargs)
                if self.current_url != "about:newtab" and \
                        not self.is_connection_error_page:
                    break
            except (TimeoutException, TimeExceededError,
                    CannotSendRequest) as last_err:
                print ("\nload_url timed out.  Attempt %s %s" %
                       ((tries + 1), last_err))
                continue
            finally:
                cancel_timeout()
        else:
            raise last_err


def launch_tor_with_config_fixture(*args, **kwargs):
    last_err = RuntimeError("Unknown error")
    for tries in range(MAX_FIXTURE_TRIES):
        try:
            timeout(LAUNCH_TOR_TIMEOUT)
            return launch_tor_with_config(*args, **kwargs)
        except TimeExceededError as last_err:
            print ("\nlaunch_tor timed out. Attempt %s %s" %
                   ((tries + 1), last_err))
            continue
        except OSError as last_err:
            print ("\nlaunch_tor try %s %s" % ((tries + 1), last_err))
            if "timeout without success" in str(last_err):
                continue
            else:
                raise
        finally:
            cancel_timeout()
    raise last_err


# We only experience timeouts on Travis CI
def raise_signal(signum, frame):
    """Raise an exception to signal timeout."""
    raise TimeExceededError("Timed out")


def timeout(duration):
    """Timeout after given duration. Linux only."""
    signal.signal(signal.SIGALRM, raise_signal)
    signal.alarm(duration)  # alarm after X seconds


def cancel_timeout():
    """Cancel the running alarm."""
    signal.alarm(0)
