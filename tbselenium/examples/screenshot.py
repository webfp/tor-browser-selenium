import sys
from os.path import dirname, join, realpath
# tbsel_dir = dirname(dirname(dirname(realpath(__file__))))
# if tbsel_dir not in sys.path:
#     sys.path.insert(0, tbsel_dir)

from tbselenium.tbdriver import TorBrowserDriver


def take_screenshot(tbb_dir):
    """Take screenshot of the page."""
    out_img = join(dirname(realpath(__file__)), "screenshot.png")
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url("https://check.torproject.org",
                        wait_for_page_body=True)
        driver.get_screenshot_as_file(out_img)
    print("Screenshot is saved as %s" % out_img)


def usage():
    print("Usage: python %s /path/to/tbb" % __file__)


def check_args():
    args = sys.argv[1:]
    if not args:
        usage()
        sys.exit(1)
    return args[0]


def main():
    tbb_dir = check_args()
    take_screenshot(tbb_dir)

if __name__ == '__main__':
    main()
