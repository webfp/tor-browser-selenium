import os
import sys
import signal
import re
import commands
from time import strftime
import distutils.dir_util as du
from log import wl_log
import psutil
from urllib2 import urlopen
from hashlib import sha256


class TimeExceededError(Exception):
    pass


def get_hash_of_directory(path):
    """Return md5 hash of the directory pointed by path."""
    from hashlib import md5
    m = md5()
    for root, _, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            for line in open(full_path).readlines():
                m.update(line)
    return m.digest()


def create_dir(dir_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def append_timestamp(_str=''):
    """Append a timestamp to a string and return it."""
    return _str + strftime('%y%m%d_%H%M%S')


def clone_dir_with_timestap(orig_dir_path):
    """Copy a folder into the same directory and append a timestamp."""
    new_dir = create_dir(append_timestamp(orig_dir_path))
    try:
        du.copy_tree(orig_dir_path, new_dir)
    except Exception, e:
        wl_log.error("Error while cloning the dir with timestamp" + str(e))
    finally:
        return new_dir


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


def is_targz_archive_corrupt(arc_path):
    # http://stackoverflow.com/a/2001749/3104416
    tar_gz_check_cmd = "gunzip -c %s | tar t > /dev/null" % arc_path
    tar_status, tar_txt = commands.getstatusoutput(tar_gz_check_cmd)
    if tar_status:
        wl_log.critical("Tar check failed: %s tar_status: %s tar_txt: %s"
                        % (tar_gz_check_cmd, tar_status, tar_txt))
        return tar_status
    return False  # no error


def pack_crawl_data(crawl_dir):
    """Compress the crawl dir into a tar archive."""
    if not os.path.isdir(crawl_dir):
        wl_log.critical("Cannot find the crawl dir: %s" % crawl_dir)
        return False
    if crawl_dir.endswith(os.path.sep):
        crawl_dir = crawl_dir[:-1]
    crawl_name = os.path.basename(crawl_dir)
    containing_dir = os.path.dirname(crawl_dir)
    os.chdir(containing_dir)
    arc_path = "%s.tar.gz" % crawl_name
    tar_cmd = "tar czvf %s %s" % (arc_path, crawl_name)
    wl_log.debug("Packing the crawl dir with cmd: %s" % tar_cmd)
    status, txt = commands.getstatusoutput(tar_cmd)
    if status or is_targz_archive_corrupt(arc_path):
        wl_log.critical("Tar command failed or archive is corrupt:\
                         %s \nSt: %s txt: %s" % (tar_cmd, status, txt))
        return False
    else:
        return True


def gen_all_children_procs(parent_pid):
    parent = psutil.Process(parent_pid)
    for child in parent.get_children(recursive=True):
        yield child


def kill_all_children(parent_pid):
    """Kill all child process of a given parent."""
    for child in gen_all_children_procs(parent_pid):
        child.kill()


def die(last_words="Unknown problem, quitting!"):
    wl_log.error(last_words)
    sys.exit(1)


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
    write_to_file(file_path, read_url(uri))


def extract_tbb_tarball(archive_path):
    arch_dir = os.path.dirname(archive_path)
    extracted_dir = os.path.join(arch_dir, "tor-browser_en-US")
    tar_cmd = "tar xvf %s -C %s" % (archive_path, arch_dir)
    status, txt = commands.getstatusoutput(tar_cmd)
    if status or not os.path.isdir(extracted_dir):
        wl_log.error("Error extracting TBB tarball %s: (%s: %s)"
                     % (tar_cmd, status, txt))
        return False
    dest_dir = archive_path.split(".tar")[0]
    mv_cmd = "mv %s %s" % (extracted_dir, dest_dir)
    status, txt = commands.getstatusoutput(mv_cmd)
    if status or not os.path.isdir(dest_dir):
        wl_log.error("Error moving extracted TBB with the command %s: (%s: %s)"
                     % (mv_cmd, status, txt))
        return False
    return True
