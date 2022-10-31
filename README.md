# tor-browser-selenium [![Build Status](https://app.travis-ci.com/webfp/tor-browser-selenium.svg?branch=main)](https://app.travis-ci.com/webfp/tor-browser-selenium)


A Python library to automate Tor Browser with Selenium.

## Installation

```
pip install tbselenium
```

Install `geckodriver` from the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases/). Make sure you install version v0.23.0 version or newer; older versions may not be compatible with the current Tor Browser series.


## Basic usage
### Using with system `tor`

`tor` needs to be installed (`apt install tor`) and running on port 9050.

```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver("/path/to/TorBrowserBundle/") as driver:
    driver.get('https://check.torproject.org')
```

### Using with `Stem`
First, make sure you have `Stem` installed (`pip install stem`).
The following will start a new `tor` process using `Stem`. It will not use the `tor` installed on your system.

```python
import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem

tbb_dir = "/path/to/TorBrowserBundle/"
tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir)
with TorBrowserDriver(tbb_dir, tor_cfg=cm.USE_STEM) as driver:
    driver.load_url("https://check.torproject.org")

tor_process.kill()
```

TorBrowserDriver does not download Tor Browser Bundle (TBB) for you. You should [download](https://www.torproject.org/projects/torbrowser.html.en), extract TBB and provide its path when you initialize `TorBrowserDriver`.

### Setting `geckodriver`'s location without using PATH
If `geckodriver` is not on the system PATH, the binary location can be set programmatically:

```python
TorBrowserDriver(executable_path="/path/to/geckodriver")
```

## Test and development
Install the Python packages that are needed for development and testing:

`pip install -r requirements-dev.txt`

Install `xvfb` package by running `apt-get install xvfb` or using your distro's package manager.

Run the following to launch the tests:

`./run_tests.py /path/to/TorBrowserBundle/`

By default, tests will be run using `Xvfb`, so the browser will not be visible.
You may disable `Xvfb` by exporting the following environment variable:

`export NO_XVFB=1`



### Running individual tests
First, export a `TBB_PATH` environment variable that points to the TBB version you want to use:

`export TBB_PATH=/path/to/tbb/tor-browser_en-US/`

Then, use `py.test` to launch the tests you want, e.g.:

* `py.test tbselenium/test/test_tbdriver.py`
* `py.test tbselenium/test/test_tbdriver.py::TBDriverTest::test_should_load_check_tpo`

### Disabling console logs
You can redirect the logs to `/dev/null` by passing the `tbb_logfile_path` initialization parameter:
```python
TorBrowserDriver(..., tbb_logfile_path='/dev/null')
```

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
[Tested](https://travis-ci.org/webfp/tor-browser-selenium) with the following Tor Browser Bundle versions on Ubuntu:

* 11.5.6
* 12.0a3

Warning: **Windows and macOS are not supported.**

## Troubleshooting

Solutions to potential issues:

* Make sure you can run Firefox on the same system. This may help discover issues such as missing libraries, displays etc..
* Outdated (or incompatible) Python `selenium` package: This is the source of various obscure errors. Make sure you have an up-to-date `selenium` package installed.
* No display: When running on a cloud machine, follow the [headless.py example](https://github.com/webfp/tor-browser-selenium/blob/master/examples/headless.py#L10) to start a virtual display.
* Outdated Tor Browser Bundle: Download and use a more recent TBB version.
* Make sure you install the latest `geckodriver` version.
* Port conflict with other (`Tor`) process: Pick a different SOCKS and controller port using `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug obscure errors. This can help with problems due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Tor Browser logs to standard output/error.
* When you use `LAUNCH_NEW_TBB_TOR` option and get the following [error message](https://github.com/webfp/tor-browser-selenium/issues/62) during the initialization, it's likely that Tor failed to bootstrap (due to network etc.):

 ```
 Can't load the profile. Profile Dir: /tmp/tmpO7i1lL/webdriver-py-profilecopy If you specified a log_file in the FirefoxBinary constructor, check it for details
 ```
* `driver.get_cookies()` returns an empty list. This is due to Private Browsing Mode (PBM), which Selenium uses under the hood. See [#79](https://github.com/webfp/tor-browser-selenium/issues/79) for a possible solution.
* WebGL is not supported in the headless mode started with `headless=True` due to Firefox bug [#1375585](https://bugzilla.mozilla.org/show_bug.cgi?id=1375585). To enable WebGL in a headless setting, use `pyvirtualdisplay` following the [headless.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/headless.py) example.

## Reference
Please consider citing this repository if you use `tor-browser-selenium` in your academic publications.

```
@misc{tor-browser-selenium,
  author = {Gunes Acar and Marc Juarez and individual contributors},
  title = {tor-browser-selenium - Tor Browser automation with Selenium},
  year = {2020},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/webfp/tor-browser-selenium}}
}
```

## Credits
We greatly benefited from the following two projects:
* [tor-browser-selenium](https://github.com/isislovecruft/tor-browser-selenium) by @isislovecruft.
* [tor-browser-bundle-testsuite](https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/) by @boklm.
