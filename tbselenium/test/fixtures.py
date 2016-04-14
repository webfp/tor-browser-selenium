import signal
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.common import TimeExceededError, TB_INIT_TIMEOUT
from selenium.common.exceptions import (TimeoutException, WebDriverException)
try:
    from httplib import CannotSendRequest
except ImportError:
    from http.client import CannotSendRequest
try:
    from stem.process import launch_tor_with_config
except ImportError as err:
    pass

MAX_FIXTURE_TRIES = 5
LAUNCH_TOR_TIMEOUT = 90
LOAD_PAGE_TIMEOUT = 60


class TorBrowserDriverFixture(TorBrowserDriver):
    """Extend TorBrowserDriver to have fixtures for tests."""
    def __init__(self, *args, **kwargs):
        last_err = RuntimeError("Unknown error")
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                timeout(TB_INIT_TIMEOUT)
                return super(TorBrowserDriverFixture, self).__init__(*args,
                                                                     **kwargs)
            except (TimeoutException, WebDriverException,
                    TimeExceededError) as last_err:
                print ("\nTBDriver init try %s %s" % ((tries + 1), last_err))
                continue
            finally:
                cancel_timeout()
        else:
            raise last_err

    def load_url_ensure(self, *args, **kwargs):
        """Make sure the requested URL is loaded. Retry if necessary."""
        last_err = RuntimeError("Unknown error")
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                timeout(LOAD_PAGE_TIMEOUT)
                self.load_url(*args, **kwargs)
                if self.current_url != "about:newtab" and \
                        not self.is_connection_error_page():
                    break
            except (TimeoutException, TimeExceededError,
                    CannotSendRequest) as last_err:
                print ("\nload_url try %s %s" % ((tries + 1), last_err))
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
            print ("\nlaunch_tor try %s %s" % ((tries + 1), last_err))
            continue
        except OSError as last_err:
            print ("\nlaunch_tor try %s %s" % ((tries + 1), last_err))
            if "timeout without success" in str(last_err.exception):
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
