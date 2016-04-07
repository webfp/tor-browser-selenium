# tor-browser-selenium [![Build Status](https://travis-ci.org/webfp/tor-browser-selenium.svg?branch=master)](https://travis-ci.org/webfp/tor-browser-selenium)

![DISCLAIMER](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Dialog-warning-orange.svg/40px-Dialog-warning-orange.svg.png "experimental")  **experimental - PLEASE BE CAREFUL**

A Python library to automate Tor Browser with Selenium.

## Requirements
Tested with the following Tor Browser Bundle versions on Debian (Wheezy) and Ubuntu (14.04 & 15.10):

* 2.4.7-alpha-1
* 3.5
* 4.0.8
* 5.5.4

Most of code should be compatible with Windows and Mac OS.

## Installation

With `apt-get`, you can install the dependencies by running the following command:

`sudo apt-get install python-setuptools git xvfb`

Clone this repository:

`git clone git@github.com:webfp/tor-browser-selenium.git`

Install:

`sudo easy_install .`

Download the Tor Browser Bundle:

You can find the latest Tor Browser Bundle here: https://www.torproject.org/projects/torbrowser.html.en. Download it and extract the tarball to a directory of your convenience (`TBB_PATH`).

## Use

```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver(TBB_PATH) as driver:
    driver.get('https://check.torproject.org')
```

where `TBB_PATH` is the path to the Tor Browser Bundle directory.


## Test

- To run all the tests: `./run_tests.py $TBB_PATH`


## Examples

In the following examples we assume the `TorBrowserDriver` class has been imported, and the `TBB_PATH` variable is the path to the Tor Browser Bundle directory.


### Simple visit to a page
```python
driver = TorBrowserDriver(TBB_PATH)
driver.get('https://check.torproject.org')
driver.quit()
```

### Simple visit using the contextmanager

```python
with TorBrowserDriver(TBB_PATH) as driver:
    driver.get('https://check.torproject.org')
    sleep(1)  # stay one second in the page
```

### Take a screenshot

Currently, we need to add an exception to access the canvas in the Tor Browser permission database. We need to do this beforehand for all the URLs that we plan to visit.

```python
with TorBrowserDriver(TBB_PATH) as driver:
    driver.get('https://check.torproject.org')
    driver.get_screenshot_as_file("screenshot.png")
```

### Visit without a virtual display

By default browser window is placed in a virtual display of dimension 1280x800.

```python
with TorBrowserDriver(TBB_PATH, virt_display=None) as driver:
    driver.get('https://check.torproject.org')  # this will show the browser window.
    sleep(1)
```

### Don't copy the profile
By default we clone the Firefox profile to isolate different sessions.
The following will not make a temporary copy of the Tor Browser profile, so that we use the same profile in different visits.

```python
with TorBrowserDriver(TBB_PATH, pollute=True) as driver:
    driver.get('https://check.torproject.org')
    sleep(1)
    # the temporary profile is wiped when driver quits
```

### Use old Tor Browser Bundles

We can use the driver with specific Tor Browser bundles by passing paths to the Tor Browser binary and profile. This is helpful for using the driver with old Tor Browser Bundles, where the directory structure is different from the one that is currently used.

In this example we used Tor Browser Bundle 3.5, which we assume has been extracted in the home directory.

```python
tbb_3_5 = join(expanduser('~'), 'tor-browser_en-US')
tb_binary = join(tbb_3_5, "Browser", "firefox")
tb_profile = join(tbb_3_5, "Data", "Browser", "profile.default")
with TorBrowserDriver(tbb_binary_path=tb_binary,
                      tbb_profile_path=tb_profile) as driver:
    driver.get('https://check.torproject.org')
```

### TorBrowserDriver + stem

This example shows how to use [stem](https://stem.torproject.org/api/control.html) to launch the `tor` process with our own configuration. We run tor with stem listening to a custom SOCKS and Controller ports, and use a particular tor binary instead of the one installed in the system.

```python
from stem.control import Controller
from stem.process import launch_tor_with_config

# If you're running tor with the TBB binary, instead
# of a tor installed in the system, you need to set
# its path in the LD_LIBRARY_PATH:
custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)

# Run tor
custom_control_port, custom_socks_port = 9051, 9050
torrc = {'ControlPort': str(custom_control_port)}
# you can add your own settings to this torrc,
# including the path and the level for logging in tor.
# you can also use the DataDirectory property in torrc
# to set a custom data directory for tor.
# For other options see: https://www.torproject.org/docs/tor-manual.html.en
tor_process = launch_tor_with_config(config=torrc, tor_cmd=custom_tor_binary)

with Controller.from_port(port=custom_control_port) as controller:
    controller.authenticate()
    # Visit the page with the TorBrowserDriver
    with TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port) as driver:
        driver.get('https://check.torproject.org')
        sleep(1)

# Kill tor process
if tor_process:
    tor_process.kill()
```

For running examples you can check the `test_examples.py` in the test directory of this repository.

## Troubleshooting

Solutions to some potential issues:

* Outdated (or incompatible) Python Selenium package: This is the source of various obscure errors. Run: `pip install -U selenium`
* Outdated Tor Browser Bundle: Download and use a more recent TBB version.
* Port conflict with other (`tor`) process: Pick a different SOCKS and controller port using `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug problems where an exception or traceback is not available or hard to understand. This can help debugging errors due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Firefox/Tor Browser logs to standard output.

```python
path_to_logfile = "ff.log"
TorBrowserDriver(TBB_PATH, tbb_logfile_path=path_to_logfile)
```

* You can disable Xvfb by setting `virt_display` argument to `None`.

## Credits
Based on FirefoxDriver and [previous code](https://github.com/isislovecruft/tor-browser-selenium) by @isislovecruft.
Some test are derived from @boklm's [tor-browser-bundle-testsuite](https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/)
Similar projects: TBD
