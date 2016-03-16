# tor-browser-selenium
Automate Tor Browser with Selenium.

## Requirements

It has been tested with Debian Wheezy and Ubuntu Trusty and Wily and the following versions of the [Tor Browser](https://www.torproject.org/projects/torbrowser.html.en):

* 2.4.7-alpha-1
* 4.0.8
* 3.5
* 5.5.3

Make sure your [Selenium](http://www.seleniumhq.org/) version supports the Firefox version on which the Tor Browser you are using is based.

Also, the system (OS, libraries, etc.) should support the Tor Browser versions used and have `Python` installed.

## Installation

Clone this repository:

`git clone git@github.com:gunesacar/tor-browser-selenium.git`

Install:

`sudo easy_install .`

Use:
```python
from tbselenium.tbdriver import TorBrowserDriver
with TorBrowserDriver(TBB_PATH) as driver:
    driver.get('https://check.torproject.org')
```

where `TBB_PATH` is the path to the Tor Browser Bundle directory.


## Test

- Tests assume there is an instance of  `tor` running.
- To run all the tests:

`./run_tests.py <path to the Tor Browser Bundle>`


## Examples

