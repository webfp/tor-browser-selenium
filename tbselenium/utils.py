import distutils.dir_util as du
from os import walk, makedirs
from os.path import join, exists
from pyvirtualdisplay import Display


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


def clone_dir_temporary(dir_path):
    """Copy a folder in the same directory and append a timestamp."""
    import tempfile
    tempdir = tempfile.mkdtemp()
    du.copy_tree(dir_path, tempdir)
    return tempdir


def start_xvfb(win_width, win_height):
    print("Starting XVFB with dimensions: %dx%d" % (win_width, win_height))
    xvfb_display = Display(visible=0, size=(win_width, win_height))
    xvfb_display.start()
    return xvfb_display


def stop_xvfb(xvfb_display):
    if xvfb_display:
        print("Stopping XVFB")
        xvfb_display.stop()
