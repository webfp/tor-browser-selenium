# tor-browser-selenium [![Build Status](https://travis-ci.org/webfp/tor-browser-selenium.svg?branch=master)](https://travis-ci.org/webfp/tor-browser-selenium)

A Python library to automate Tor Browser with Selenium.

## Compatibility
[Tested](https://travis-ci.org/webfp/tor-browser-selenium) with the following Tor Browser Bundle versions on Debian (Wheezy) and Ubuntu (14.04 & 15.10):

* 4.0.8
* 5.5.4
* 6.0a4

## Installation and use

```
git clone git@github.com:webfp/tor-browser-selenium.git
pip install .
```

[Download](https://www.torproject.org/projects/torbrowser.html.en) and extract Tor Browser Bundle and provide its path when you initialize `TorBrowserDriver`.

```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver(TBB_PATH) as driver:
    driver.get('https://check.torproject.org')
```

where `TBB_PATH` is the path to the Tor Browser Bundle directory.


## Test

- To run all the tests: `./run_tests.py /path/to/TBB`


## Examples

### Simple visit to a page
```python
driver = TorBrowserDriver("/path/to/tbb")
driver.get('https://check.torproject.org')
driver.quit()
```

### Simple visit using the contextmanager

```python
with TorBrowserDriver("/path/to/tbb") as driver:
    driver.get('https://check.torproject.org')
    sleep(1)  # stay one second in the page
```

### Take a screenshot

```python
with TorBrowserDriver("/path/to/tbb") as driver:
    driver.get('https://check.torproject.org')
    driver.get_screenshot_as_file("screenshot.png")
```

For TBB versions older than 4.5a3 you may get a blank screenshot, due to an issue with Tor Browser's canvas fingerprinting defenses.
You may add an exception for the site(s) you want to visit by passing their URLs in `canvas_exceptions` list:

```python
with TorBrowserDriver("/path/to/tbb", canvas_exceptions=["https://torproject.org"]) as driver:
    driver.get('https://check.torproject.org')
    driver.get_screenshot_as_file("screenshot.png")
```

### Using old Tor Browser Bundles

If you want to use TBB version 3.X and older you need to initialize TorBrowserDriver with the paths for Tor Browser binary and profile (instead of the TBB folder).
This is due to changes in the TBB directory structure; old versions have different directory structure than the current one.

For instance, for Tor Browser Bundle 3.5:

```python
tbb_3_5 = join('/some/path', 'tor-browser_en-US')
tb_binary = join(tbb_3_5, "Browser", "firefox")
tb_profile = join(tbb_3_5, "Data", "Browser", "profile.default")
with TorBrowserDriver(tbb_binary_path=tb_binary,
                      tbb_profile_path=tb_profile) as driver:
    driver.get('https://check.torproject.org')
```

### TorBrowserDriver + Stem
This example shows how TorBrowserDriver can use a running Tor process started with [Stem](https://stem.torproject.org/api/control.html).

```python
from stem.control import Controller
from stem.process import launch_tor_with_config

custom_tor_binary = join(TBB_PATH, cm.DEFAULT_TOR_BINARY_PATH)
environ["LD_LIBRARY_PATH"] = dirname(custom_tor_binary)

custom_control_port, custom_socks_port = 9051, 9050
torrc = {'ControlPort': str(custom_control_port)}
tor_process = launch_tor_with_config(config=torrc, tor_cmd=custom_tor_binary)

with Controller.from_port(port=custom_control_port) as controller:
    controller.authenticate()
    # Tell TorBrowserDriver to use SOCKS port to 
    with TorBrowserDriver(TBB_PATH, socks_port=custom_socks_port,
                          tor_cfg=cm.USE_RUNNING_TOR) as driver:
        driver.get('https://check.torproject.org')

# Kill tor process
if tor_process:
    tor_process.kill()
```

Check `test_examples.py` for more examples.

## Troubleshooting

Solutions to some potential issues:

* Outdated (or incompatible) Python Selenium package: This is the source of various obscure errors. Run: `pip install -U selenium`
* Outdated Tor Browser Bundle: Download and use a more recent TBB version.
* Port conflict with other (`Tor`) process: Pick a different SOCKS and controller port using `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug problems where an exception or traceback is not available or hard to understand. This can help debugging errors due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Firefox/Tor Browser logs to standard output.

```python
path_to_logfile = "ff.log"
TorBrowserDriver(TBB_PATH, tbb_logfile_path=path_to_logfile)
```

## Credits
* [isislovecruft/tor-browser-selenium](https://github.com/isislovecruft/tor-browser-selenium).
* [tor-browser-bundle-testsuite](https://gitweb.torproject.org/boklm/tor-browser-bundle-testsuite.git/) by @boklm.

