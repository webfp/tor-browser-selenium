import commands
import distutils.dir_util as du
import re
import signal
from hashlib import sha256
from os import walk, makedirs
from os.path import join, exists
from time import strftime
from urllib2 import urlopen


class TimeExceededError(Exception):
    pass


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


def create_dir(dir_path):
    """Create a directory if it doesn't exist."""
    if not exists(dir_path):
        makedirs(dir_path)
    return dir_path


def append_timestamp(_str=''):
    """Append a timestamp to a string and return it."""
    return _str + strftime('%y%m%d_%H%M%S')


def clone_dir_with_timestap(dir_path):
    """Copy a folder into the same directory and append a timestamp."""
    new_dir = create_dir(append_timestamp(dir_path))
    du.copy_tree(dir_path, new_dir)


def raise_signal(signum, frame):
    raise TimeExceededError


def timeout(duration):
    """Timeout after given duration."""
    signal.signal(signal.SIGALRM, raise_signal)  # linux only !!!
    signal.alarm(duration)  # alarm after X seconds


def cancel_timeout():
    """Cancel a running alarm."""
    signal.alarm(0)


def get_filename_from_url(url, prefix):
    """Return base filename for the url."""
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.replace('www.', '')
    dashed = re.sub(r'[^A-Za-z0-9._]', '-', url)
    return '%s-%s' % (prefix, re.sub(r'-+', '-', dashed))


def read_file(path, binary=False):
    """Read and return the file content."""
    options = 'rb' if binary else 'rU'
    with open(path, options) as f:
        return f.read()


def sha_256_sum_file(path, binary=True):
    """Return the SHA-256 sum of the file."""
    return sha256(read_file(path, binary=binary)).hexdigest()


def gen_read_lines(path):
    """Generator for reading the lines in a file."""
    with open(path, 'rU') as f:
        for line in f:
            yield line


def read_url(uri):
    """Fetch and return a URI content."""
    w = urlopen(uri)
    return w.read()


def write_to_file(file_path, data):
    """Write data to file and close."""
    with open(file_path, 'w') as ofile:
        ofile.write(data)


def download_file(uri, file_path):
    print("Will download %s to %s" % (uri, file_path))
    write_to_file(file_path, read_url(uri))


def extract_tarball(tarball_path, parent_path, flags='xvf'):
    tar_cmd = "tar %s %s -C %s" % (flags, tarball_path, parent_path)
    status, txt = commands.getstatusoutput(tar_cmd)
    if status:
        Exception("Error extracting TBB tarball %s: (%s: %s)"
                  % (tar_cmd, status, txt))
