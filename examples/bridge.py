from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from time import sleep

# Usage: python bridge.py /path/to/tor-browser-bundle bridge_type
# bridge_type is one of: obfs3, obfs4, fte, meek-amazon, meek-azure


def visit_using_bridge(tbb_dir, bridge_type="meek-amazon"):
    url = "https://check.torproject.org"
    with TorBrowserDriver(
            tbb_dir, default_bridge_type=bridge_type) as driver:
        driver.load_url(url)
        print driver.find_element_by("h1.on").text  # status text
        sleep(10)  # To verify that the bridge is indeed uses, go to
        # Tor Network Settings dialog


def main():
    desc = "Visit check.torproject.org website using a Tor bridge"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    parser.add_argument('bridge_type', nargs='?', default="meek-amazon")
    args = parser.parse_args()
    visit_using_bridge(args.tbb_path, args.bridge_type)


if __name__ == '__main__':
    main()
