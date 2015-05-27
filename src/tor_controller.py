import os
import shutil
from stem.control import Controller
import stem.process
from stem.util import term
import common as cm
import utils as ut


class TorController(object):
    def __init__(self, torrc_dict, tbb_version, tor_log='/dev/null'):
        self.torrc_dict = torrc_dict
        self.controller = None
        self.tbb_version = tbb_version
        self.tmp_tor_data_dir = None
        self.tor_process = None
        self.log_file = tor_log

    def tor_log_handler(self, line):
        print(term.format(line))

    def restart_tor(self):
        """Kill current Tor process and run a new one."""
        self.kill_tor_proc()
        self.launch_tor_service(self.log_file)

    def kill_tor_proc(self):
        """Kill Tor process."""
        if self.tor_process:
            print("Killing tor process")
            self.tor_process.kill()
        if self.tmp_tor_data_dir and os.path.isdir(self.tmp_tor_data_dir):
            print("Removing tmp tor data dir")
            shutil.rmtree(self.tmp_tor_data_dir)

    def launch_tor_service(self, logfile='/dev/null'):
        """Launch Tor service and return the process."""
        self.log_file = logfile
        self.tmp_tor_data_dir = ut.clone_dir_with_timestap(
            cm.get_tor_data_path(self.tbb_version))

        self.torrc_dict.update({'DataDirectory': self.tmp_tor_data_dir,
                                'Log': ['INFO file %s' % logfile]})

        print("Tor config: %s" % self.torrc_dict)
        # the following may raise, make sure it's handled
        self.tor_process = stem.process.launch_tor_with_config(
            config=self.torrc_dict,
            init_msg_handler=self.tor_log_handler,
            tor_cmd=cm.get_tor_bin_path(self.tbb_version),
            timeout=270
            )
        self.controller = Controller.from_port()
        self.controller.authenticate()
        print("Tor running at port {0} & controller port {1}."
              .format(cm.SOCKS_PORT, cm.CONTROLLER_PORT))
        return self.tor_process

    def close_all_streams(self):
        """Close all streams of a controller."""
        print("Closing all streams")
        try:
            ut.timeout(cm.STREAM_CLOSE_TIMEOUT)
            for stream in self.controller.get_streams():
                print("Closing stream %s %s %s " %
                      (stream.id, stream.purpose, stream.target_address))
                self.controller.close_stream(stream.id)  # MISC reason
        except ut.TimeExceededError:
            print("Closing streams timed out!")
        except:
            print("Exception closing stream")
        finally:
            ut.cancel_timeout()
