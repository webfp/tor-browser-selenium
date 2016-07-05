# tor-browser-selenium [![Build Status](https://travis-ci.org/webfp/tor-browser-selenium.svg?branch=master)](https://travis-ci.org/webfp/tor-browser-selenium)

A Python library to automate Tor Browser with Selenium.

## Installation and use

```
git clone git@github.com:webfp/tor-browser-selenium.git
pip install .
```

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
Use the [examples](https://github.com/webfp/tor-browser-selenium/tree/master/examples) to discover different ways to use TorBrowserDriver
* [check_tpo.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/check_tpo.py): Visit check.torproject.org website and print the network status message
* [headless.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/headless.py): Headless visit and screenshot of check.torproject.org using XVFB
* [hidden_service.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/hidden_service.py): Search using DuckDuckGo's hidden service
* [parallel.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/parallel.py): Visit check.torproject.org website running 3 browsers in parallel
* [screenshot.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/screenshot.py): Take a screenshot using TorBrowserDriver
* [stem_simple.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/stem_simple.py): Simple use of Stem with the TorBrowserDriver
* [stem_adv.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/stem_adv.py): Simple use of Stem with the TorBrowserDriver with more advanced configuration


## Compatibility
[Tested](https://travis-ci.org/webfp/tor-browser-selenium) with the following Tor Browser Bundle versions on Debian (Wheezy) and Ubuntu (14.04 & 15.10):

* 4.0.8
* 5.5.5
* 6.0.2

## Troubleshooting

Solutions to potential issues:

* Outdated (or incompatible) Python Selenium package: This is the source of various obscure errors. Run: `pip install -U selenium`
* Outdated Tor Browser Bundle: Download and use a more recent TBB version.
* Port conflict with other (`Tor`) process: Pick a different SOCKS and controller port using `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug problems where an exception or traceback is not available or hard to understand. This can help debugging errors due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Firefox/Tor Browser logs to standard output.

```python
path_to_logfile = "ff.log"
TorBrowserDriver(TBB_PATH, tbb_logfile_path=path_to_logfile)
```

## Credits
We greatly benefited from the following two projects:
* [tor-browser-selenium](https://github.com/isislovecruft/tor-browser-selenium) by @isislovecruft.
* [tor-browser-bundle-testsuite](https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/) by @boklm.

