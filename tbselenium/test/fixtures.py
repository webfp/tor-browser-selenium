import signal
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.common import TimeExceededError, TB_INIT_TIMEOUT
from selenium.common.exceptions import (TimeoutException, WebDriverException)
try:
    from stem.process import launch_tor_with_config
except ImportError as err:
    pass

MAX_FIXTURE_TRIES = 3
LAUNCH_TOR_TIMEOUT = 90
LOAD_PAGE_TIMEOUT = 60


class TorBrowserDriverFixture(TorBrowserDriver):
    """Extend TorBrowserDriver to have fixtures for tests."""
    def __init__(self, *args, **kwargs):
        for _ in range(MAX_FIXTURE_TRIES):
            try:
                timeout(TB_INIT_TIMEOUT)
                return super(TorBrowserDriverFixture, self).__init__(*args,
                                                                     **kwargs)
            except (TimeoutException, WebDriverException,
                    TimeExceededError) as exc:
                continue
            finally:
                cancel_timeout()
        else:
            raise exc

    def load_url_ensure(self, *args, **kwargs):
        """Make sure the requested URL is loaded. Retry if necessary."""
        last_err = None
        for _ in range(MAX_FIXTURE_TRIES):
            try:
                timeout(LOAD_PAGE_TIMEOUT)
                self.load_url(*args, **kwargs)
                if self.current_url != "about:newtab" and \
                        not self.is_connection_error_page():
                    break
            except (TimeoutException, TimeExceededError) as last_err:
                continue
            finally:
                cancel_timeout()
        else:
            if last_err:
                raise last_err
            else:
                raise TimeoutException("Can't load the page.")


def launch_tor_with_config_fixture(*args, **kwargs):
    for _ in range(MAX_FIXTURE_TRIES):
        try:
            timeout(LAUNCH_TOR_TIMEOUT)
            return launch_tor_with_config(*args, **kwargs)
        except (OSError, TimeExceededError) as exc:
            if "second timeout without success" in str(exc.exception):
                continue
            else:
                raise
        finally:
            cancel_timeout()
    raise exc


# We only experience timeouts on Travis CI
def raise_signal(signum, frame):
    """Raise an exception to signal timeout."""
    raise TimeExceededError


def timeout(duration):
    """Timeout after given duration. Linux only."""
    signal.signal(signal.SIGALRM, raise_signal)
    signal.alarm(duration)  # alarm after X seconds


def cancel_timeout():
    """Cancel the running alarm."""
    signal.alarm(0)
