from argparse import ArgumentParser
from os.path import dirname, join, realpath
from tbselenium.tbdriver import TorBrowserDriver


def take_screenshot(tbb_dir, url):
    """Take screenshot of the page."""
    out_img = join(dirname(realpath(__file__)), "screenshot.png")
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url(url, wait_for_page_body=True)
        driver.get_screenshot_as_file(out_img)
    print("Screenshot is saved as %s" % out_img)


def main():
    parser = ArgumentParser(description="Take a screenshot using Tor Browser")
    parser.add_argument('tbb_path')
    parser.add_argument('url', nargs='?',
                        default="https://check.torproject.org")
    args = parser.parse_args()
    take_screenshot(args.tbb_path, args.url)

if __name__ == '__main__':
    main()
