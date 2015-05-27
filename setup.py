import os
import common as cm
import subprocess
import utils as ut
from log import wl_log


def get_tbb_filename(tbb_ver):
    if int(tbb_ver.split(".")[0]) <= 2:
        file_name = 'tor-browser-gnu-linux-%s-%s-dev-en-US.tar.gz' %\
            (cm.machine, tbb_ver)
    else:
        file_name = 'tor-browser-linux%s-%s_en-US.tar.xz' % (cm.arch, tbb_ver)
    return file_name


def get_tbb_base_url(tbb_ver):
    archive_url = "https://archive.torproject.org/tor-package-archive/torbrowser/"  # noqa
    if int(tbb_ver.split(".")[0]) <= 2:
        base_url = "%slinux/" % (archive_url)
    else:
        base_url = "%s%s/" % (archive_url, tbb_ver)
    return base_url


def get_url_by_tbb_ver(tbb_ver):
    base_url = get_tbb_base_url(tbb_ver)
    tbb_tarball_url = "%s%s" % (base_url, get_tbb_filename(tbb_ver))
    return tbb_tarball_url


def download_tbb_tarball(tbb_ver, dl_dir=""):
    tbb_url = get_url_by_tbb_ver(tbb_ver)
    base_dir = dl_dir if dl_dir else cm.TBB_BASE_DIR
    tarball_path = os.path.join(base_dir, get_tbb_filename(tbb_ver))
    if not os.path.isfile(tarball_path):
        wl_log.info("Will download %s to %s" % (tbb_url, tarball_path))
        ut.download_file(tbb_url, tarball_path)
        ut.extract_tbb_tarball(tarball_path)
    if verify_tbb_tarball(tbb_ver, tarball_path, tbb_url):
        return tarball_path
    # we cannot verify the integrity of the downloaded tarball
    raise cm.TBBTarballVerificationError("Cannot verify the integrity of %s"
                                         % tarball_path)


def verify_tbb_sig(sig_file):
    """Verify the ."""
    ret_code = subprocess.Popen(['/usr/bin/gpg',
                                 '--verify', sig_file]).wait()
    return True if ret_code == 0 else False


def verify_tbb_tarball(tbb_ver, tarball_path, tbb_url):
    tarball_filename = get_tbb_filename(tbb_ver)
    tarball_sha_sum = ut.sha_256_sum_file(tarball_path).lower()
    sha_sum_url = "%s%s" % (get_tbb_base_url(tbb_ver), "sha256sums.txt")
    sha_sum_path = "%s%s" % (tarball_path, ".sha256sums.txt")
    sha_sum_sig_url = "%s%s" % (sha_sum_url, ".asc")
    sha_sum_sig_path = "%s%s" % (sha_sum_path, ".asc")
    if not os.path.isfile(sha_sum_path):
        ut.download_file(sha_sum_url, sha_sum_path)
    if not os.path.isfile(sha_sum_sig_path):
        ut.download_file(sha_sum_sig_url, sha_sum_sig_path)

    if not verify_tbb_sig(sha_sum_sig_path):
        return False

    # https://github.com/micahflee/torbrowser-launcher/blob/3f1146e1a084c4e8021da968104cbc2877ae01e6/torbrowser_launcher/launcher.py#L560
    for line in ut.gen_read_lines(sha_sum_path):
        if tarball_sha_sum in line.lower() and tarball_filename in line:
            return True
    return False


def import_gpg_key(key_fp):
    """Import GPG key with the given fingerprint."""
    wl_log.info("Will import the GPG key %s" % key_fp)
    # https://www.torproject.org/docs/verifying-signatures.html.en
    ret_code = subprocess.Popen(['/usr/bin/gpg', '--keyserver',
                                 'x-hkp://pool.sks-keyservers.net',
                                 '--recv-keys', key_fp]).wait()
    return True if ret_code == 0 else False


def import_tbb_signing_keys():
    """Import signing GPG keys for TBB."""
    tbb_devs_key = '0x4E2C6E8793298290'
    erinns_key = '0x416F061063FEE659'  # old key
    if import_gpg_key(tbb_devs_key) and import_gpg_key(erinns_key):
        return True
    else:
        raise cm.TBBSigningKeyImportError("Cannot import TBB signing keys")


def get_recommended_tbb_version():
    """Get the recommended TBB version from RecommendedTBBVersions file."""
    tbb_versions_url = "https://www.torproject.org/projects/torbrowser/RecommendedTBBVersions"  # noqa
    versions = ut.read_url(tbb_versions_url)
    for line in versions.split():
        if "Linux" in line:
            return line.split("-")[0].lstrip('"')
    raise cm.TBBGetRecommendedVersionError()


def setup_env():
    """Initialize the tbb directory and import TBB signing keys.

    Download recommended TBB version and verify it.
    """
    import_tbb_signing_keys()
    ut.create_dir(cm.TBB_BASE_DIR)
    tbb_rec_ver = get_recommended_tbb_version()
    download_tbb_tarball(tbb_rec_ver)

if __name__ == '__main__':
    setup_env()
