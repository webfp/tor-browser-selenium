from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.support.ui import Select
from time import sleep


def visit(tbb_dir):
    url = "https://check.torproject.org"
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url(url)
        # Iterate over a bunch of locales from the drop-down menu
        for lang_code in ["en_US", "fr", "zh_CN", "fa", "ru", "hi", "ja"]:
            select = Select(driver.find_element_by_id("cl"))
            select.select_by_value(lang_code)
            sleep(1)
            print("\n======== Locale: %s ========" % lang_code)
            print driver.find_element_by("h1.on").text  # status text
            print driver.find_element_by(".content > p").text  # IP address


def main():
    desc = "Visit check.torproject.org website"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    visit(args.tbb_path)


if __name__ == '__main__':
    main()
