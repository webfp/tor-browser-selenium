from selenium.webdriver.common.keys import Keys
from xvfbwrapper import Xvfb
from torutils import TorBrowserDriver
from log import wl_log
import os
import common as cm
from dumputils import Sniffer
import time
import utils as ut


BAREBONE_HOME_PAGE = "file://%s/barebones.html" % cm.ETC_DIR

VBOX_GATEWAY_IP = "10.0.2.2"  # default gateway IP of VirtualBox
LXC_GATEWAY_IP = "10.0.3.1"  # default gateway IP of LXC
LOCALHOST_IP = "127.0.0.1"  # default localhost IP


class Visit(object):
    """Hold info about a particular visit to a page."""

    def __init__(self, batch_num, site_num, instance_num, page_url,
                 base_dir, tbb_version, tor_controller, bg_site=None,
                 experiment=cm.EXP_TYPE_WANG_AND_GOLDBERG, xvfb=False,
                 capture_screen=True):
        self.batch_num = batch_num
        self.site_num = site_num
        self.instance_num = instance_num
        self.page_url = page_url
        self.bg_site = bg_site
        self.experiment = experiment
        self.base_dir = base_dir
        self.visit_dir = None
        self.visit_log_dir = None
        self.tbb_version = tbb_version
        self.capture_screen = capture_screen
        self.tor_controller = tor_controller
        self.xvfb = xvfb
        self.init_visit_dir()
        self.pcap_path = os.path.join(
            self.visit_dir, "{}.pcap".format(self.get_instance_name()))

        if self.xvfb and not cm.running_in_CI:
            wl_log.info("Starting XVFBm %sX%s" % (cm.XVFB_W, cm.XVFB_H))
            self.vdisplay = Xvfb(width=cm.XVFB_W, height=cm.XVFB_H)
            self.vdisplay.start()

        # Create new instance of TorBrowser driver
        self.tb_driver = TorBrowserDriver(
            tbb_logfile_path=os.path.join(
                self.visit_dir, "logs", "firefox.log"),
            tbb_version=tbb_version,
            page_url=page_url)

        self.sniffer = Sniffer()  # sniffer to capture the network traffic

    def init_visit_dir(self):
        """Create results and logs directories for this visit."""
        visit_name = str(self.instance_num)
        self.visit_dir = os.path.join(self.base_dir, visit_name)
        ut.create_dir(self.visit_dir)
        self.visit_log_dir = os.path.join(self.visit_dir, 'logs')
        ut.create_dir(self.visit_log_dir)

    def get_instance_name(self):
        """Construct and return a filename for the instance."""
        inst_file_name = '{}_{}_{}'\
            .format(self.batch_num, self.site_num, self.instance_num)
        return inst_file_name

    def cleanup_visit(self):
        """Kill sniffer and Tor browser if they're running."""
        wl_log.info("Cleaning up visit.")
        wl_log.info("Cancelling timeout")
        ut.cancel_timeout()

        if self.sniffer and self.sniffer.is_recording:
            wl_log.info("Stopping sniffer...")
            self.sniffer.stop_capture()
        if self.tb_driver and self.tb_driver.is_running:
            # shutil.rmtree(self.tb_driver.prof_dir_path)
            wl_log.info("Quitting selenium driver...")
            self.tb_driver.quit()

        # close all open streams to prevent pollution
        self.tor_controller.close_all_streams()
        if self.xvfb and not cm.running_in_CI:
            self.vdisplay.stop()

    def take_screenshot(self):
        try:
            out_png = os.path.join(self.visit_dir, 'screenshot.png')
            wl_log.info("Taking screenshot of %s to %s" % (self.page_url,
                                                           out_png))
            self.tb_driver.get_screenshot_as_file(out_png)
            if cm.running_in_CI:
                wl_log.debug("Screenshot data:image/png;base64,%s"
                             % self.tb_driver.get_screenshot_as_base64())
        except:
            wl_log.info("Exception while taking screenshot of: %s"
                        % self.page_url)

    def get_wang_and_goldberg(self):
        """Visit the site according to Wang and Goldberg (WPES'13) settings."""
        ut.timeout(cm.HARD_VISIT_TIMEOUT)  # set timeout to stop the visit

        self.sniffer.start_capture(
            self.pcap_path,
            'tcp and not host %s and not host %s and not host %s'
            % (VBOX_GATEWAY_IP, LOCALHOST_IP, LXC_GATEWAY_IP))

        time.sleep(cm.PAUSE_BETWEEN_INSTANCES)
        try:
            self.tb_driver.set_page_load_timeout(cm.SOFT_VISIT_TIMEOUT)
        except:
            wl_log.info("Exception setting a timeout {}".format(self.page_url))

        wl_log.info("Crawling URL: {}".format(self.page_url))

        t1 = time.time()
        self.tb_driver.get(self.page_url)
        page_load_time = time.time() - t1
        wl_log.info("{} loaded in {} sec"
                    .format(self.page_url, page_load_time))
        time.sleep(cm.WAIT_IN_SITE)
        if self.capture_screen:
            self.take_screenshot()
        self.cleanup_visit()

    def get_multitab(self):
        """Open two tab, use one to load a background site and the other to
        load the real site."""
        PAUSE_BETWEEN_TAB_OPENINGS = 0.5
        ut.timeout(cm.HARD_VISIT_TIMEOUT)  # set timeout to kill running procs
        # load a blank page - a page is needed to send keys to the browser
        self.tb_driver.get(BAREBONE_HOME_PAGE)
        self.sniffer.start_capture(self.pcap_path,
                                   'tcp and not host %s and not host %s'
                                   % (VBOX_GATEWAY_IP, LOCALHOST_IP))

        time.sleep(cm.PAUSE_BETWEEN_INSTANCES)
        try:
            self.tb_driver.set_page_load_timeout(cm.SOFT_VISIT_TIMEOUT)
        except:
            wl_log.info("Exception setting a timeout {}".format(self.page_url))

        wl_log.info("Crawling URL: {} with {} in the background".
                    format(self.page_url, self.bg_site))

        body = self.tb_driver.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')  # open a new tab
        # now that the focus is on the address bar, load the background
        # site by "typing" it to the address bar and "pressing" ENTER (\n)
        # simulated by send_keys function
        body.send_keys('%s\n' % self.bg_site)

        # the delay between the loading of background and real sites
        time.sleep(PAUSE_BETWEEN_TAB_OPENINGS)

        body = self.tb_driver.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')  # open a new tab

        t1 = time.time()
        self.tb_driver.get(self.page_url)  # load the real site in the 2nd tab

        page_load_time = time.time() - t1
        wl_log.info("{} loaded in {} sec"
                    .format(self.page_url, page_load_time))
        time.sleep(cm.WAIT_IN_SITE)
        if self.capture_screen:
            self.take_screenshot()
        self.cleanup_visit()

    def get(self):
        """Call the specific visit function depending on the experiment."""
        if self.experiment == cm.EXP_TYPE_WANG_AND_GOLDBERG:
            self.get_wang_and_goldberg()
        elif self.experiment == cm.EXP_TYPE_MULTITAB_ALEXA:
            self.get_multitab()
        else:
            raise ValueError("Cannot determine experiment type")
