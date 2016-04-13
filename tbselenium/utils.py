import commands
import sqlite3
from os import walk
from os.path import join
import fnmatch
from hashlib import sha256


def get_hash_of_directory(dir_path):
    """Return sha256 hash of the directory pointed by path."""
    m = sha256()
    for file_path in gen_find_files(dir_path):
        m.update(read_file(file_path))
    return m.digest()


def gen_find_files(dir_path, pattern="*"):
    """Return filenames that matches the given pattern under a given dir
    http://www.dabeaz.com/generators/
    """
    for path, _, filelist in walk(dir_path):
        for name in fnmatch.filter(filelist, pattern):
            yield join(path, name)


def read_file(file_path, mode='rU'):
    """Read and return file content."""
    with open(file_path, mode) as f:
        content = f.read()
    return content


def is_png(path):
    # Taken from http://stackoverflow.com/a/21555489
    data = read_file(path, 'rb')
    return (data[:8] == '\211PNG\r\n\032\n'and (data[12:16] == 'IHDR'))


def run_cmd(cmd):
    return commands.getstatusoutput('%s ' % cmd)


def add_canvas_permission(profile_path, canvas_allowed_hosts):
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
    for host in canvas_allowed_hosts:
        qry = """INSERT INTO 'moz_hosts'
        VALUES(NULL,'%s','canvas/extractData',1,0,0,0,0);""" % host
        cursor.execute(qry)
    perm_db.commit()
    cursor.close()
