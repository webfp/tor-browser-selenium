# tor-browser-selenium
Automate Tor Browser with Selenium.


## Installation

Clone this repository:

`git clone git@github.com:gunesacar/tor-browser-selenium.git`

Install:

`sudo easy_install .`

Use:
```
from tbselenium import tbdriver
tbdriver.TorBrowserDriver(TBB_PATH)
tbdriver.get('https://google.com')
```

where TBB_PATH is the path to the Tor Browser Bundle directory.


## Test

- Tests assume there is an instance of  `tor` running.
- Set `TBB_PATH` environment variable to the path of a Tor Browser Bundle:
    `export TBB_PATH=<path to tor browser bundle>`
- `Xvfb` can be used for testing:
    ```
    Xvfb :1 -screen 5 1024x768x8 &;
    export DISPLAY=:1.5
    ```
- run `tbselenium/test/`.



## More info

See the `RunDriverWithControllerTest` in `test_torcontroller` for an example on how to use the Tor Browser driver with
the TorController.
