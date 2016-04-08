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

```
apt-get install python-setuptools git xvfb
git clone git@github.com:webfp/tor-browser-selenium.git
sudo easy_install .
```

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

```python
with TorBrowserDriver(TBB_PATH) as driver:
    driver.get('https://check.torproject.org')
    driver.get_screenshot_as_file("screenshot.png")
```

For TBB versions older than 4.5a3 you may get a blank screenshot, due to an issue with Tor Browser's canvas fingerprinting defenses.
You may add an exception for the site(s) you want to visit by passing their URLs in `canvas_exceptions` list:

```python
with TorBrowserDriver(TBB_PATH, canvas_exceptions=["https://torproject.org"]) as driver:
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

### Using old Tor Browser Bundles

If you want to use old TBB versions (<=V4.X) initialize TorBrowserDriver with the paths for Tor Browser binary and profile (instead of the TBB folder).
This is due to changes in the TBB directory structure; old versions have different directory structure than the current one.

In this example we used Tor Browser Bundle 3.5.

```python
tbb_3_5 = join('/some/path', 'tor-browser_en-US')
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
