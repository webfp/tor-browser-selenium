import os
import logging

LOG_PREFIX = 'webfp'


def reset_logger(logger):
    """Remove all the handlers for a logger."""
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()

        elif isinstance(handler, logging.StreamHandler):
            handler.flush()

        # print "****handler removed****"
        logger.removeHandler(handler)


def add_log_file_handler(logger, filename):
    fh = logging.FileHandler(filename)
    frmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_level = logger.getEffectiveLevel()  # get global log level
    init_log_handler(fh, logger, log_level, frmt)


def init_log_handler(handler, logger, level, frmt):
    """ Initialize log handler."""
    handler.setLevel(level)
    handler.setFormatter(frmt)
    logger.addHandler(handler)


def get_logger(logname, logtype='fc', level=logging.DEBUG,
               frmt=None, filename=''):
    """Create and return a logger with the given name.

    logtype f: file, c: console, fc: both

    """
    logger = logging.getLogger(logname)
    logger.setLevel(level)
    frmt = frmt or logging.Formatter('%(asctime)s - \
                    %(levelname)s - %(message)s')

    if 'f' in logtype:
        log_filename = filename if filename else 'crawl.log'
        fh = logging.FileHandler(log_filename)

        init_log_handler(fh, logger, level, frmt)

    if 'c' in logtype:
        ch = logging.StreamHandler()
        init_log_handler(ch, logger, level, frmt)

    return logger


def add_symlink(linkname, src_file):
    """Create a symbolic link pointing to src_file"""
    if os.path.lexists(linkname):   # check and remove if link exists
        try:
            os.unlink(linkname)
        except:
            pass
    try:
        os.symlink(src_file, linkname)
    except:
        print "Cannot create symlink!"

wl_log = get_logger(LOG_PREFIX, logtype='c')
