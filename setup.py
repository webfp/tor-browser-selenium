import os
import subprocess
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "src"))
import common as cm
import utils as ut
from urllib2 import HTTPError

SHA_SUMS_FILENAME = "sha256sums.txt"
SHA_SUMS_UNSIGNED_FILENAME = "sha256sums-unsigned-build.txt"


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
    tarball_url = get_url_by_tbb_ver(tbb_ver)
    tarball_sig_url = tarball_url + ".asc"
    base_dir = dl_dir if dl_dir else cm.TBB_BASE_DIR
    tarball_path = os.path.join(base_dir, get_tbb_filename(tbb_ver))
    tarball_sig_path = tarball_path + ".asc"

    if not os.path.isfile(tarball_path):
        ut.download_file(tarball_url, tarball_path)
        ut.download_file(tarball_sig_url, tarball_sig_path)

    if not verify_gpg_sig(tarball_sig_path):
        raise cm.TBBTarballVerificationError("Cannot verify GPG signature of %s"
                                     % tarball_sig_path)

    if not verify_tarball_shasum(tbb_ver, tarball_path, tarball_url):
        raise cm.TBBTarballVerificationError("Cannot verify the integrity of %s"
                                     % tarball_path)
    dest_dir = tarball_path.split(".tar")[0]
    if not os.path.isdir(dest_dir):
        ut.extract_tbb_tarball(tarball_path)
    return tarball_path
    # we cannot verify the integrity of the downloaded tarball


def verify_gpg_sig(sig_file):
    """Verify the GPG signature."""
    TBB_DEVS_SIGNINGKEY_FP = "EF6E286DDA85EA2A4BA7DE684E2C6E8793298290"
    ERINNS_SIGNINGKEY_FP = "8738A680B84B3031A630F2DB416F061063FEE659"

    # http://tor.stackexchange.com/questions/648/how-to-verify-tor-browser-bundle-tbb-3-x#comment821_667
    gpg_sig_status_file = "gpg_sig_status_file.txt"
    ret_code = subprocess.Popen(['/usr/bin/gpg',
                                 '--verify', '--status-file', gpg_sig_status_file, sig_file]).wait()
    if not os.path.isfile(gpg_sig_status_file):
        print "Cannot find the GPG verification status output file", gpg_sig_status_file
        return False
    ver_status = ut.read_file(gpg_sig_status_file)
    os.remove(gpg_sig_status_file)
    if "GOODSIG" in ver_status and "VALIDSIG" in ver_status and\
        ((TBB_DEVS_SIGNINGKEY_FP in ver_status) or
         (ERINNS_SIGNINGKEY_FP in ver_status)):
        print "Verified the GPG signature for", sig_file
        return True
    else:
        print "GPG verification error for", sig_file, ver_status
        return False


def sig_path(path):
    """Return the .asc signature path for a given path or URL."""
    return path + ".asc"


def download_shasum_for_tbb_ver(tbb_ver, tarball_path):
    sha_sum_url = "%s%s" % (get_tbb_base_url(tbb_ver), SHA_SUMS_FILENAME)
    sha_sum_path = "%s.%s" % (tarball_path, SHA_SUMS_FILENAME)
    sha_sum_unsigned_path = "%s.%s" % (tarball_path, SHA_SUMS_UNSIGNED_FILENAME)

    if not os.path.isfile(sha_sum_path) and not os.path.isfile(sha_sum_unsigned_path):
        print "Cannot find the shasums file, will download"
        try:
            ut.download_file(sha_sum_url, sha_sum_path)
            ut.download_file(sig_path(sha_sum_url), sig_path(sha_sum_path))
            return sha_sum_path
        except HTTPError:
            # Try the new shasums scheme
            sha_sum_unsigned_url = "%s%s" % (get_tbb_base_url(tbb_ver), SHA_SUMS_UNSIGNED_FILENAME)
            print "Failed to download", sha_sum_url, "will try", sha_sum_unsigned_url
            try:
                ut.download_file(sha_sum_unsigned_url, sha_sum_unsigned_path)
                ut.download_file(sig_path(sha_sum_unsigned_url), sig_path(sha_sum_unsigned_path))
                return sha_sum_unsigned_path
            except HTTPError:
                print "Failed to download, will fail!", sha_sum_unsigned_url
                return False



def verify_tarball_shasum(tbb_ver, tarball_path, tarball_url):
    # https://www.torproject.org/docs/verifying-signatures.html.en#BuildVerification
    tarball_filename = get_tbb_filename(tbb_ver)
    tarball_sha_sum = ut.sha_256_sum_file(tarball_path).lower()
    sha_sum_path = download_shasum_for_tbb_ver(tbb_ver, tarball_path)
    if not sha_sum_path or not os.path.isfile(sha_sum_path):
        print "Can't find sha_sum file at", sha_sum_path
        return False

    if not verify_gpg_sig(sig_path(sha_sum_path)):
        return False

    # https://github.com/micahflee/torbrowser-launcher/blob/3f1146e1a084c4e8021da968104cbc2877ae01e6/torbrowser_launcher/launcher.py#L560
    for line in ut.gen_read_lines(sha_sum_path):
        if tarball_sha_sum in line.lower() and tarball_filename in line:
            return True
    return False


def import_gpg_key(key_fp):
    """Import GPG key with the given fingerprint."""
    print("Will import the GPG key %s" % key_fp)
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
    import sys
    version = None
    if len(sys.argv) == 2:
        version = sys.argv[1]
    if not version:
        version = get_recommended_tbb_version()
    import_tbb_signing_keys()
    ut.create_dir(cm.TBB_BASE_DIR)
    download_tbb_tarball(version)

if __name__ == '__main__':
    setup_env()
