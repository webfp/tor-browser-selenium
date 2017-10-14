from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
from os.path import join, dirname, realpath


def headless_visit(tbb_dir):
    out_img = join(dirname(realpath(__file__)), "headless_screenshot.png")
    # start a virtual display
    xvfb_display = start_xvfb()
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url("https://check.torproject.org")
        driver.get_screenshot_as_file(out_img)
        print("Screenshot is saved as %s" % out_img)

    stop_xvfb(xvfb_display)


def main():
    desc = "Headless visit and screenshot of check.torproject.org using XVFB"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    headless_visit(args.tbb_path)


if __name__ == '__main__':
    main()
