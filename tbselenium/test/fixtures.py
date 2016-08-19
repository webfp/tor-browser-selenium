from socket import error as socket_error
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.exceptions import StemLaunchError, TorBrowserDriverInitError
from tbselenium.utils import launch_tbb_tor_with_stem, is_busy, read_file
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from httplib import CannotSendRequest
except ImportError:
    from http.client import CannotSendRequest


MAX_FIXTURE_TRIES = 3

DEBUG = False


class TBDriverFixture(TorBrowserDriver):
    """Extend TorBrowserDriver to have fixtures for tests."""
    def __init__(self, *args, **kwargs):
        self.change_default_tor_cfg(kwargs)
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                return super(TBDriverFixture, self).__init__(*args, **kwargs)
            except (TimeoutException, WebDriverException, socket_error) as last_err:
                print ("\nTBDriver init error. Attempt %s %s" %
                       ((tries + 1), last_err))
                if DEBUG and "tbb_logfile_path" in kwargs:
                    print(read_file(kwargs.get("tbb_logfile_path")))
                super(TBDriverFixture, self).quit()  # clean up
                continue
        # Raise if we didn't return yet
        to_raise = last_err if last_err else\
            TorBrowserDriverInitError("Cannot initialize")
        raise to_raise

    def change_default_tor_cfg(self, kwargs):
        """Use system Tor if the caller doesn't specifically wants
        to launch a new TBB Tor.

        This makes tests faster and more robust against network
        issues since otherwise we'd have to launch a new Tor process
        for each test.
        """

        if kwargs.get("tor_cfg") is None and is_busy(cm.DEFAULT_SOCKS_PORT):
            kwargs["tor_cfg"] = cm.USE_RUNNING_TOR

    def load_url_ensure(self, *args, **kwargs):
        """Make sure the requested URL is loaded. Retry if necessary."""
        for tries in range(MAX_FIXTURE_TRIES):
            try:
                self.load_url(*args, **kwargs)
                if self.current_url != "about:newtab" and \
                        not self.is_connection_error_page:
                    return
            except (TimeoutException,
                    CannotSendRequest) as last_err:
                print ("\nload_url timed out.  Attempt %s %s" %
                       ((tries + 1), last_err))
                continue
        # Raise if we didn't return yet
        to_raise = last_err if last_err else\
            WebDriverException("Can't load the page")
        raise to_raise


def launch_tbb_tor_with_stem_fixture(*args, **kwargs):
    for tries in range(MAX_FIXTURE_TRIES):
        try:
            return launch_tbb_tor_with_stem(*args, **kwargs)
        except OSError as last_err:
            print ("\nlaunch_tor try %s %s" % ((tries + 1), last_err))
            if "timeout without success" in str(last_err):
                continue
            else:  # we don't want to retry if this is not a timeout
                raise
    # Raise if we didn't return yet
    to_raise = last_err if last_err else\
        StemLaunchError("Cannot start Tor")
    raise to_raise
