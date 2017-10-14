from argparse import ArgumentParser
from os.path import dirname, join, realpath, getsize
from tbselenium.tbdriver import TorBrowserDriver


def visit_and_capture(tbb_dir, url):
    """Take screenshot of the page."""
    out_img = join(dirname(realpath(__file__)), "screenshot.png")
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url(url, wait_for_page_body=True)
        driver.get_screenshot_as_file(out_img)
    print("Screenshot is saved as %s (%s bytes)" % (out_img, getsize(out_img)))


def main():
    desc = "Take a screenshot using TorBrowserDriver"
    default_url = "https://check.torproject.org"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    parser.add_argument('url', nargs='?', default=default_url)
    args = parser.parse_args()
    visit_and_capture(args.tbb_path, args.url)


if __name__ == '__main__':
    main()
