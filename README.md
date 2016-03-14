# tor-browser-selenium
Automate Tor Browser with Selenium.


## Installation

Clone this repository:

`git@github.com:gunesacar/tor-browser-selenium.git`

Install:

`sudo easy_install .`

Use:
```
from tbselenium import tbdriver
tbdriver.TorBrowserDriver(TBB_PATH)
```

where TBB_PATH is the path to the Tor Browser Bundle directory.


## Test

Set `TBB_PATH` environment variable to the path of a Tor Browser Bundle.



## More info

See the `RunDriverWithControllerTest` in `test_torcontroller` for an example on how to use the Tor Browser driver with
the TorController.
