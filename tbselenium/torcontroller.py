from os import environ
from os.path import join, isfile, isdir, dirname
import shutil

import stem.process
from stem.control import Controller
from stem.util import term

import common as cm
import utils as ut


class TorController(object):
    def __init__(self,
                 tbb_path=None,
                 tor_binary_path=None,
                 tor_data_path=None,
                 torrc_dict={'SocksPort': str(cm.DEFAULT_SOCKS_PORT)},
                 tor_log='/dev/null'):
        assert (tbb_path or tor_binary_path and tor_data_path)
        if tbb_path:
            tbb_path = tbb_path.rstrip('/')
            tor_binary_path = join(tbb_path, cm.DEFAULT_TOR_BINARY_PATH)
            tor_data_path = join(tbb_path, cm.DEFAULT_TOR_DATA_PATH)

        # Make sure the paths exist
        assert (isfile(tor_binary_path) and isdir(tor_data_path))
        self.tor_binary_path = tor_binary_path
        self.tor_data_path = tor_data_path
        self.torrc_dict = torrc_dict
        self.controller = None
        self.tmp_tor_data_dir = None
        self.tor_process = None
        self.log_file = tor_log
        self.export_lib_path()

    def tor_log_handler(self, line):
        print(term.format(line))

    def restart_tor(self):
        """Kill current Tor process and run a new one."""
        self.kill_tor_proc()
        self.launch_tor_service(self.log_file)

    def export_lib_path(self):
        """Add the Tor Browser binary to the library path."""
        environ["LD_LIBRARY_PATH"] = dirname(self.tor_binary_path)

    def kill_tor_proc(self):
        """Kill Tor process."""
        if self.tor_process:
            print("Killing tor process")
            self.tor_process.kill()
        if self.tmp_tor_data_dir and isdir(self.tmp_tor_data_dir):
            print("Removing tmp tor data dir")
            shutil.rmtree(self.tmp_tor_data_dir)

    def launch_tor_service(self, logfile='/dev/null'):
        """Launch Tor service and return the process."""
        self.log_file = logfile
        self.tmp_tor_data_dir = ut.clone_dir_with_timestap(self.tor_data_path)

        self.torrc_dict.update({'ControlPort': str(cm.REFACTOR_CONTROL_PORT),
                                'DataDirectory': self.tmp_tor_data_dir,
                                'Log': ['INFO file %s' % logfile]})

        print("Tor config: %s" % self.torrc_dict)
        # the following may raise, make sure it's handled
        self.tor_process = stem.process.launch_tor_with_config(
            config=self.torrc_dict,
            init_msg_handler=self.tor_log_handler,
            tor_cmd=self.tor_binary_path,
            timeout=270
        )
        self.controller = Controller.from_port(port=cm.REFACTOR_CONTROL_PORT)
        self.controller.authenticate()
        print("Tor running at port {0} & controller port {1}."
              .format(cm.DEFAULT_SOCKS_PORT, cm.REFACTOR_CONTROL_PORT))
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
