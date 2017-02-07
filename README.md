# tor-browser-selenium [![Build Status](https://travis-ci.org/webfp/tor-browser-selenium.svg?branch=master)](https://travis-ci.org/webfp/tor-browser-selenium)

A Python library to automate Tor Browser with Selenium.

## Installation

```
pip install tbselenium
```
## Basic usage
```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver("/path/to/TorBrowserBundle/") as driver:
    driver.get('https://check.torproject.org')
```

TorBrowserDriver does not download Tor Browser Bundle (TBB) for you. You should [download](https://www.torproject.org/projects/torbrowser.html.en) and extract TBB and provide its path when you initialize `TorBrowserDriver`.

## Test and development
Install the Python packages needed for development and testing:

`pip install requirements-dev.txt`

Run the following to launch the tests:

`./run_tests.py /path/to/TorBrowserBundle/`


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
[Tested](https://travis-ci.org/webfp/tor-browser-selenium) with the following Tor Browser Bundle versions on Debian (Wheezy) and Ubuntu (14.04 & 15.10):

* 6.5
* 6.5a3
* 5.5.5
* 4.0.8

## Troubleshooting

Solutions to potential issues:

* Outdated (or incompatible) Python Selenium package: This is the source of various obscure errors. Run: `pip install -U selenium`
* Outdated Tor Browser Bundle: Download and use a more recent TBB version.
* Port conflict with other (`Tor`) process: Pick a different SOCKS and controller port using `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug obscure errors. This can help with errors due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Tor Browser logs to standard output.
* When you use `LAUNCH_NEW_TBB_TOR` option and get the following [error message](https://github.com/webfp/tor-browser-selenium/issues/62) during the initialization, it's likely that Tor failed to bootstrap:

 ```
 Can't load the profile. Profile Dir: /tmp/tmpO7i1lL/webdriver-py-profilecopy If you specified a log_file in the FirefoxBinary constructor, check it for details
 ```

## Credits
We greatly benefited from the following two projects:
* [tor-browser-selenium](https://github.com/isislovecruft/tor-browser-selenium) by @isislovecruft.
* [tor-browser-bundle-testsuite](https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/) by @boklm.
