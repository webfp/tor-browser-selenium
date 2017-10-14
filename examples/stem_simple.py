from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem


def launch_tb_with_stem(tbb_dir):
    tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir)
    with TorBrowserDriver(tbb_dir,
                          tor_cfg=cm.USE_RUNNING_TOR,
                          socks_port=cm.STEM_SOCKS_PORT,
                          control_port=cm.STEM_CONTROL_PORT) as driver:
        driver.load_url("https://check.torproject.org", wait_on_page=3)
        print(driver.find_element_by("h1.on").text)
        print(driver.find_element_by(".content > p").text)

    tor_process.kill()


def main():
    desc = "Use TorBrowserDriver with Stem"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    launch_tb_with_stem(args.tbb_path)


if __name__ == '__main__':
    main()
