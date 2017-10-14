from argparse import ArgumentParser
from stem.control import Controller
from stem import CircStatus
from tbselenium.tbdriver import TorBrowserDriver
import tbselenium.common as cm
from tbselenium.utils import launch_tbb_tor_with_stem
from selenium.webdriver.common.utils import free_port
import tempfile
from os.path import join


def print_tor_circuits(controller):
    """Print built Tor circuits using Stem.
    From https://stem.torproject.org/tutorials/examples/list_circuits.html
    """
    for circ in sorted(controller.get_circuits()):
        if circ.status != CircStatus.BUILT:
            continue

        print("\nCircuit %s (%s)" % (circ.id, circ.purpose))

        for i, entry in enumerate(circ.path):
            div = '+' if (i == len(circ.path) - 1) else '|'
            fingerprint, nickname = entry

            desc = controller.get_network_status(fingerprint, None)
            address = desc.address if desc else 'unknown'

            print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))


def launch_tb_with_custom_stem(tbb_dir):
    socks_port = free_port()
    control_port = free_port()
    tor_data_dir = tempfile.mkdtemp()
    tor_binary = join(tbb_dir, cm.DEFAULT_TOR_BINARY_PATH)
    print("SOCKS port: %s, Control port: %s" % (socks_port, control_port))

    torrc = {'ControlPort': str(control_port),
             'SOCKSPort': str(socks_port),
             'DataDirectory': tor_data_dir}
    tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_dir, torrc=torrc,
                                           tor_binary=tor_binary)
    with Controller.from_port(port=control_port) as controller:
        controller.authenticate()
        with TorBrowserDriver(tbb_dir, socks_port=socks_port,
                              control_port=control_port,
                              tor_cfg=cm.USE_RUNNING_TOR) as driver:
            driver.load_url("https://check.torproject.org", wait_on_page=3)
            print(driver.find_element_by("h1.on").text)
            print(driver.find_element_by(".content > p").text)
        print_tor_circuits(controller)

    tor_process.kill()


def main():
    desc = "Use TorBrowserDriver with Stem"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    launch_tb_with_custom_stem(args.tbb_path)


if __name__ == '__main__':
    main()
