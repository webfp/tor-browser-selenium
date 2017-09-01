from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from time import sleep

BRIDGE_TYPE_PREF = "extensions.torlauncher.default_bridge_type"


def visit(tbb_dir):
    url = "https://check.torproject.org"
    with TorBrowserDriver(
        tbb_dir, pref_dict={BRIDGE_TYPE_PREF: "meek-amazon"}) as driver:
        driver.load_url(url)
        print driver.find_element_by("h1.on").text  # status text
        # Leave some time to check the Tor circuit interface to
        sleep(10)  # verify that the bridge is really used.
         


def main():
    desc = "Visit check.torproject.org website using a Tor bridge"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    visit(args.tbb_path)

if __name__ == '__main__':
    main()
