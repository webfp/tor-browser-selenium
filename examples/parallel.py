from multiprocessing import Pool
from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import launch_tbb_tor_with_stem
from tbselenium.common import STEM_SOCKS_PORT, USE_RUNNING_TOR,\
    STEM_CONTROL_PORT

JOBS_IN_PARALLEL = 3


def run_in_parallel(inputs, worker, no_of_processes=JOBS_IN_PARALLEL):
    p = Pool(no_of_processes)
    p.map(worker, inputs)


def visit_check_tpo_with_stem(tbb_dir):
    url = "https://check.torproject.org"
    with TorBrowserDriver(tbb_dir,
                          socks_port=STEM_SOCKS_PORT,
                          control_port=STEM_CONTROL_PORT,
                          tor_cfg=USE_RUNNING_TOR) as driver:
        driver.load_url(url, wait_on_page=3)
        print(driver.find_element_by("h1.on").text)
        print(driver.find_element_by(".content > p").text)


def launch_browsers_in_parallel(tbb_path):
    tor_process = launch_tbb_tor_with_stem(tbb_path=tbb_path)
    run_in_parallel(JOBS_IN_PARALLEL * [tbb_path],
                    visit_check_tpo_with_stem)
    tor_process.kill()


def main():
    desc = "Visit check.torproject.org website running 3 browsers in parallel"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    launch_browsers_in_parallel(args.tbb_path)


if __name__ == '__main__':
    main()
