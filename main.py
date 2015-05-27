import argparse
import traceback
import logging
import common as cm
import sys
from log import wl_log
import utils as ut
from datacollection.crawler import Crawler


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Crawl a list of URLs \
            in several batches.')
    # list of urls to be crawled
    parser.add_argument('-u', '--url-list', help='URL list file path')
    parser.add_argument('-b', '--browser-version', help="Tor browser's version"
                        "used to crawl, possible values are: "
                        "'wang_and_goldberg' (%s) or 'last_stable' "
                        "(default: last_stable (%s))"
                        % (cm.TBB_WANG_AND_GOLDBERG, cm.TBB_DEFAULT_VERSION),
                        default=cm.TBB_DEFAULT_VERSION)
    parser.add_argument('-v', '--verbose', help='increase output verbosity',
                        action='store_true')
    parser.add_argument("-e", "--experiment", help="Experiment type. Possible"
                        " values are: 'wang_and_goldberg', 'multitab_alexa'")

    # For understanding batch and instance parameters please refer to Wang and
    # Goldberg WPES'13 paper, Section 4.1.4
    parser.add_argument('--batch', help='Number of batches (default: %s)'
                        % cm.NUM_BATCHES, default=cm.NUM_BATCHES)
    parser.add_argument('--instance', help='Number of instances (default: %s)'
                        % cm.NUM_INSTANCES, default=cm.NUM_INSTANCES)

    parser.add_argument('--start', help='Crawl URLs after this line (1)')
    parser.add_argument('--stop', help='Crawl URLs until this line')
    parser.add_argument('--action', help='Type of action: crawl, pack_data')
    parser.add_argument('-i', '--input', help='Input data (crawl dir, etc. )')
    parser.add_argument('-x', '--xvfb', help='Use XVFB (for headless testing)',
                        action='store_true', default=False)
    parser.add_argument('-c', '--capture-screen',
                        help='Capture page screenshots',
                        action='store_true', default=False)

    args = parser.parse_args()
    action = args.action
    if action == "pack_data":
        path = args.input
        ut.pack_crawl_data(path)
        sys.exit(0)

    url_list_path = args.url_list
    verbose = args.verbose
    tbb_version = args.browser_version
    experiment = args.experiment
    no_of_batches = int(args.batch)
    no_of_instances = int(args.instance)
    start_line = int(args.start) if args.start else 1
    stop_line = int(args.stop) if args.stop else 999999999999
    xvfb = args.xvfb
    capture_screen = args.capture_screen
    if verbose:
        wl_log.setLevel(logging.DEBUG)
    else:
        wl_log.setLevel(logging.INFO)

    # Validate the given arguments
    # Read urls
    url_list = []
    import os
    if not url_list_path or not os.path.isfile(url_list_path):
        ut.die("ERROR: No URL list given!"
               "Run the following to get help: python main --help")
    else:
        try:
            with open(url_list_path) as f:
                url_list = f.read().splitlines()[start_line - 1:stop_line]
        except Exception as e:
            ut.die("Error opening file: {} \n{}"
                   .format(e, traceback.format_exc()))

    if experiment == cm.EXP_TYPE_WANG_AND_GOLDBERG:
        torrc_dict = cm.TORRC_WANG_AND_GOLDBERG
    elif experiment == cm.EXP_TYPE_MULTITAB_ALEXA:
        torrc_dict = cm.TORRC_DEFAULT
    else:
        ut.die("Experiment type is not recognized."
               " Use --help to see the possible values.")

    if not tbb_version:
        # Assign the last stable version of TBB
        tbb_version = cm.TBB_DEFAULT_VERSION
    elif tbb_version not in cm.TBB_KNOWN_VERSIONS:
        ut.die("Version of Tor browser is not recognized."
               " Use --help to see which are the accepted values.")

    crawler = Crawler(torrc_dict, url_list, tbb_version,
                      experiment, xvfb, capture_screen)
    wl_log.info("Command line parameters: %s" % sys.argv)

    # Run the crawl
    try:
        crawler.crawl(no_of_batches, no_of_instances,
                      start_line=start_line - 1)
    except KeyboardInterrupt:
        wl_log.warning("Keyboard interrupt! Quitting...")
    except Exception as e:
        wl_log.error("Exception: \n%s"
                     % (traceback.format_exc()))
    finally:
        crawler.stop_crawl()
