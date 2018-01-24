# tor-browser-selenium [![Build Status](https://travis-ci.org/webfp/tor-browser-selenium.svg?branch=master)](https://travis-ci.org/webfp/tor-browser-selenium)

A Python library to automate Tor Browser with Selenium.

## Installation

```
pip install tbselenium
```

You also need to install **geckodriver v0.17.0** from the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases/tag/v0.17.0). Make sure you install the v0.17.0 version; newer or older versions will not be compatible with the current Tor Browser series.

Test your `geckodriver` installation by running the command below; it must return `geckodriver 0.17.0`:
```
geckodriver --version
```

## Basic usage
```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver("/path/to/TorBrowserBundle/") as driver:
    driver.get('https://check.torproject.org')
```

TorBrowserDriver does not download Tor Browser Bundle (TBB) for you. You should [download](https://www.torproject.org/projects/torbrowser.html.en) and extract TBB and provide its path when you initialize `TorBrowserDriver`.

## Test and development
Install the Python packages that are needed for development and testing:

`pip install -r requirements-dev.txt`

Install `xvfb` package by running `apt-get install xvfb` or using your distro's package manager.

Run the following to launch the tests:

`./run_tests.py /path/to/TorBrowserBundle/`

By default, tests will be run using `Xvfb`, so the browser will not be visible.
You may disable `Xvfb` by exporting the following environment variable:

`export NO_XVFB=1`



#### Running individual tests
First, export a `TBB_PATH` environment variable that points to the TBB version you want to use:

`export TBB_PATH=/path/to/tbb/tor-browser_en-US/`

Then, use `py.test` to launch the tests you want, e.g.:

* `py.test tbselenium/test/test_tbdriver.py`
* `py.test tbselenium/test/test_tbdriver.py::TBDriverTest::test_should_load_check_tpo`


## Examples
Check the [examples](https://github.com/webfp/tor-browser-selenium/tree/master/examples) to discover different ways to use TorBrowserDriver
* [check_tpo.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/check_tpo.py): Visit check.torproject.org website and print the network status message
* [headless.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/headless.py): Headless visit and screenshot of check.torproject.org using XVFB
* [hidden_service.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/hidden_service.py): Search using DuckDuckGo's hidden service
* [parallel.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/parallel.py): Visit check.torproject.org with 3 browsers running in parallel
* [screenshot.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/screenshot.py): Take a screenshot
* [stem_simple.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/stem_simple.py): Using Stem to start the Tor process
* [stem_adv.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/stem_adv.py): Using Stem with more advanced configuration


## Compatibility
[Tested](https://travis-ci.org/webfp/tor-browser-selenium) with the following Tor Browser Bundle versions on Debian and Ubuntu:

* 7.5
* 8.0a1
* 6.5.1

Windows and macOS are not supported.

## Troubleshooting

Solutions to potential issues:

* Outdated (or incompatible) Python `selenium` package: This is the source of various obscure errors. Make sure you have `selenium` version **3.3** or above.
* Outdated Tor Browser Bundle: Download and use a more recent TBB version.
* Try an older geckodriver version that matches the current Firefox version number inside the Tor Browser Bundle.
* Port conflict with other (`Tor`) process: Pick a different SOCKS and controller port using `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug obscure errors. This can help with problems due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Tor Browser logs to standard output.
* When you use `LAUNCH_NEW_TBB_TOR` option and get the following [error message](https://github.com/webfp/tor-browser-selenium/issues/62) during the initialization, it's likely that Tor failed to bootstrap (due to network etc.):

 ```
 Can't load the profile. Profile Dir: /tmp/tmpO7i1lL/webdriver-py-profilecopy If you specified a log_file in the FirefoxBinary constructor, check it for details
 ```
* `driver.get_cookies()` returns an empty list. This is due to Private Browsing Mode (PBM), which Selenium uses under the hood. See [#79](https://github.com/webfp/tor-browser-selenium/issues/79) for a possible solution.

## Credits
We greatly benefited from the following two projects:
* [tor-browser-selenium](https://github.com/isislovecruft/tor-browser-selenium) by @isislovecruft.
* [tor-browser-bundle-testsuite](https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/) by @boklm.
