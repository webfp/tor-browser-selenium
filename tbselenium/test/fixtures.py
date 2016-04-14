from tbselenium.tbdriver import TorBrowserDriver
from selenium.common.exceptions import (TimeoutException,
                                        WebDriverException)
try:
    from stem.process import launch_tor_with_config
except ImportError as err:
    pass

MAX_FIXTURE_TRIES = 3


class TorBrowserDriverFixture(TorBrowserDriver):
    """Extend TorBrowserDriver to have fixtures for tests."""
    def __init__(self, *args, **kwargs):
        for _ in range(MAX_FIXTURE_TRIES):
            try:
                return super(TorBrowserDriverFixture, self).__init__(*args,
                                                                     **kwargs)
            except (TimeoutException, WebDriverException) as exc:
                continue
        else:
            raise exc

    def load_url_ensure(self, *args, **kwargs):
        """Make sure the requested URL is loaded. Retry if necessary."""
        last_err = None
        for _ in range(MAX_FIXTURE_TRIES):
            try:
                self.load_url(*args, **kwargs)
                if self.current_url != "about:newtab" and \
                        not self.is_connection_error_page():
                    break
            except TimeoutException as last_err:
                continue
        else:
            if last_err:
                raise last_err
            else:
                raise TimeoutException("Can't load the page.")


def launch_tor_with_config_fixture(*args, **kwargs):
    for _ in range(MAX_FIXTURE_TRIES):
        try:
            return launch_tor_with_config(*args, **kwargs)
        except (OSError) as exc:
            if "second timeout without success" in str(exc.exception):
                continue
            else:
                raise
    raise exc
