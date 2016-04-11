import commands
import sqlite3
import distutils.dir_util as du
from os import walk, makedirs
from os.path import join, exists
import common as cm
from pyvirtualdisplay import Display
import fnmatch


def get_hash_of_directory(path):
    """Return md5 hash of the directory pointed by path."""
    from hashlib import md5
    m = md5()
    for root, _, files in walk(path):
        for f in files:
            full_path = join(root, f)
            for line in open(full_path).readlines():
                m.update(line)
    return m.digest()


def gen_find_files(dir_path, pattern="*"):
    """Returns filenames that matches the given pattern under a given dir
    http://www.dabeaz.com/generators/
    """
    for path, _, filelist in walk(dir_path):
        for name in fnmatch.filter(filelist, pattern):
            yield join(path, name)


def create_dir(dir_path):
    """Create directory with the given path if it doesn't exist."""
    if not exists(dir_path):
        makedirs(dir_path)
    return dir_path


def clone_dir_temporary(dir_path):
    """Copy a folder to the same directory and append a timestamp."""
    import tempfile
    tempdir = tempfile.mkdtemp()
    du.copy_tree(dir_path, tempdir)
    return tempdir


def start_xvfb(win_width=cm.DEFAULT_XVFB_WIN_W,
               win_height=cm.DEFAULT_XVFB_WIN_H):
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    if xvfb_display:
        xvfb_display.stop()


def read_file(path, mode='rU'):
    """Read and return file content."""
    with open(path, mode) as f:
        content = f.read()
    return content


def is_png(path):
    # Taken from http://stackoverflow.com/a/21555489
    data = read_file(path, 'rb')
    return (data[:8] == '\211PNG\r\n\032\n'and (data[12:16] == 'IHDR'))


def run_cmd(cmd):
    return commands.getstatusoutput('%s ' % cmd)


def is_port_listening(port_no):
    cmd = "netstat -atn | grep %s" % port_no
    _, output = run_cmd(cmd)
    return "LISTEN" in output


def add_canvas_permission(profile_path, canvas_exceptions):
    """Create a permission db (permissions.sqlite) and add
    exceptions for the canvas image extraction for the given domains.
    If we don't add permissions, screenshots taken by TBB < 4.5a3 will be
    blank images due to the canvas fingerprinting defense in the Tor
    Browser.

    Canvas permission is only needed for TBB < 4.5a3.

    With TBB versions >= 4.5a3, chrome scripts are exempted from the
    canvas permission, so Selenium code that grabs the canvas image (which
    should appear as a chrome script) does not require a separate
    permission.

    See, https://trac.torproject.org/projects/tor/ticket/13439
    """
    connect_to_db = sqlite3.connect
    perm_db = connect_to_db(join(profile_path, "permissions.sqlite"))
    cursor = perm_db.cursor()
    # http://mxr.mozilla.org/mozilla-esr31/source/build/automation.py.in
    cursor.execute("PRAGMA user_version=3")
    cursor.execute("""CREATE TABLE IF NOT EXISTS moz_hosts (
      id INTEGER PRIMARY KEY,
      host TEXT,
      type TEXT,
      permission INTEGER,
      expireType INTEGER,
      expireTime INTEGER,
      appId INTEGER,
      isInBrowserElement INTEGER)""")
    for domain in canvas_exceptions:
        qry = """INSERT INTO 'moz_hosts'
        VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % domain
        cursor.execute(qry)
    perm_db.commit()
    cursor.close()
