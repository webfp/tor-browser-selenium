# tor-browser-selenium [![Build Status](https://app.travis-ci.com/webfp/tor-browser-selenium.svg?branch=main)](https://app.travis-ci.com/webfp/tor-browser-selenium)


A Python library to automate Tor Browser with Selenium WebDriver.

## 📦 Installation

> [!WARNING]
> Windows and macOS are currently not supported.

```
pip install tbselenium
```

Download `geckodriver` v0.31.0 from the [geckodriver releases page](https://github.com/mozilla/geckodriver/releases/) and add it to PATH.

## 🚀 Usage

Download and extract [Tor Browser](https://www.torproject.org/projects/torbrowser.html.en), and pass its folder's path when you initialize `TorBrowserDriver`. In the examples below, you should not pass "/path/to/tor-browser/", but the (Tor Browser) folder that contains the directory called `Browser`:


### Using with system `tor`

`tor` needs to be installed (`apt install tor`) and running on port 9050.

```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver("/path/to/tor-browser/") as driver:
    driver.get('https://check.torproject.org')
```

### Using with `Stem`
You can use `Stem` to start a new tor process programmatically, and connect to it from `tor-browser-selenium`. Make sure you have `Stem` installed: `pip install stem`:


```python
import tbselenium.common as cm
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem

tbb_dir = "/path/to/tor-browser/"
tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir)
with TorBrowserDriver(tbb_dir, tor_cfg=cm.USE_STEM) as driver:
    driver.load_url("https://check.torproject.org")

tor_process.kill()
```


## 💡 Examples
Check the [examples](https://github.com/webfp/tor-browser-selenium/tree/master/examples) to discover different ways to use `tor-browser-selenium`
* [check_tpo.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/check_tpo.py): Visit the `check.torproject.org` website and print the network status message
* [headless.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/headless.py): Headless visit and screenshot of check.torproject.org using [PyVirtualDisplay](https://pypi.org/project/PyVirtualDisplay/)
* [onion_service.py](https://github.com/webfp/tor-browser-selenium/blob/main/examples/onion_service.py): Search using DuckDuckGo's Onion service
* [parallel.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/parallel.py): Visit `check.torproject.org`` with 3 browsers running in parallel
* [screenshot.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/screenshot.py): Take a screenshot
* [stem_simple.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/stem_simple.py): Use Stem to start a `tor` process
* [stem_adv.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/stem_adv.py): Use Stem to launch `tor` with more advanced configuration



## 🛠️ Test and development

* Browse the [existing tests](https://github.com/webfp/tor-browser-selenium/tree/main/tbselenium/test) to find out about different ways you can use `tor-browser-selenium`.

* For development and testing first install the necessary Python packages:
  `pip install -r requirements-dev.txt`

* Install the `xvfb` package by running `apt-get install xvfb` or using your distro's package manager.

* Run the following to launch the tests:

  `./run_tests.py /path/to/tor-browser/`

* By default, tests will be run using `Xvfb`, so the browser window will not be visible.
You may disable `Xvfb` by setting the `NO_XVFB` environment variable:

  `export NO_XVFB=1`


### Running individual tests
* First, export the path to Tor Browser folder in the `TBB_PATH` environment variable.

`export TBB_PATH=/path/to/tbb/tor-browser/`

* Then, use `py.test` to launch the tests you want, e.g.:

* `py.test tbselenium/test/test_tbdriver.py`
* `py.test tbselenium/test/test_tbdriver.py::TBDriverTest::test_should_load_check_tpo`


### Using a custom `geckodriver`
A custom `geckodriver` binary can be set via the `executable_path` argument:

```python
TorBrowserDriver(executable_path="/path/to/geckodriver")
```

### Disabling console logs
You can redirect the logs to `/dev/null` by passing the `tbb_logfile_path` initialization parameter:
```python
TorBrowserDriver(..., tbb_logfile_path='/dev/null')
```

## ⚙️ Compatibility

Warning: **Windows and macOS are not supported.**

[Tested](https://travis-ci.org/webfp/tor-browser-selenium) with the following Tor Browser versions on Ubuntu:

* **Stable**: 13.5.7
* **Alpha**: 14.0a9

If you need to use a different version of Tor Browser, [view the past test runs](https://travis-ci.org/webfp/tor-browser-selenium) to find out the compatible `selenium` and `geckodriver` versions.

## 🔧 Troubleshooting

Solutions to potential issues:

* Make sure you have compatible dependencies. While older or newer versions may work, they may cause issues.
  - [Tor Browser](https://www.torproject.org/download/) needs to be downloaded and extracted.
  - Python [`selenium`](https://www.selenium.dev/) (`pip install -U selenium`).
  - `geckodriver` [version 0.31.0](https://github.com/mozilla/geckodriver/releases/tag/v0.31.0).

* Running Firefox on the same system may help diagnose issues such as missing libraries and displays.
* `Process unexpectedly closed with status 1`: If you encounter this on a remote machine you connect via SSH, you may need to enable the [headless mode](https://github.com/webfp/tor-browser-selenium/blob/master/examples/headless.py).
* Port conflict with other (`Tor`) process: Pick a different SOCKS and controller port using the `socks_port` argument.
* Use `tbb_logfile_path` argument of TorBrowserDriver to debug obscure errors. This can help with problems due to missing display, missing libraries (e.g. when the LD_LIBRARY_PATH is not set correctly) or other errors that Tor Browser logs to standard output/error.
* `driver.get_cookies()` returns an empty list. This is due to Private Browsing Mode (PBM), which Selenium uses under the hood. See [#79](https://github.com/webfp/tor-browser-selenium/issues/79) for a possible solution.
* WebGL is not supported in the headless mode started with `headless=True` due to a Firefox bug ([#1375585](https://bugzilla.mozilla.org/show_bug.cgi?id=1375585)). To enable WebGL in a headless setting, use `pyvirtualdisplay` following the [headless.py](https://github.com/webfp/tor-browser-selenium/tree/master/examples/headless.py) example.

## 📚 Reference
Please use the following reference if you use `tor-browser-selenium` in your academic publications.

```
@misc{tor-browser-selenium,
  author = {Gunes Acar and Marc Juarez and individual contributors},
  title = {tor-browser-selenium - Tor Browser automation with Selenium},
  year = {2023},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/webfp/tor-browser-selenium}}
}
```

## 🙌 Credits
We greatly benefited from the [tor-browser-bundle-testsuite](https://gitlab.torproject.org/tpo/applications/tor-browser-bundle-testsuite) and [tor-browser-selenium](https://github.com/isislovecruft/tor-browser-selenium) projects.
