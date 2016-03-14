import unittest
from time import sleep

from tld import get_tld

import tbselenium.utils as ut


class UtilsTest(unittest.TestCase):
    def test_timeout(self):
        ut.timeout(1)
        try:
            sleep(1.1)
        except ut.TimeExceededError:
            pass  # this is what we want
        else:
            self.fail("Cannot set timeout")

    def test_cancel_timeout(self):
        ut.timeout(1)
        ut.cancel_timeout()
        try:
            sleep(1.1)
        except ut.TimeExceededError:
            self.fail("Cannot cancel timeout")

    def test_get_public_suffix(self):
        urls = ('http://www.foo.org',
                'https://www.foo.org',
                'http://www.subdomain.foo.org',
                'http://www.subdomain.foo.org:80/subfolder',
                'https://www.subdomain.foo.org:80/subfolder?p1=4545&p2=54545',
                'https://www.subdomain.foo.org:80/subfolder/baefasd==/65')
        for pub_suf_test_url in urls:
            self.assertEqual(get_tld(pub_suf_test_url),
                             "foo.org")


if __name__ == "__main__":
    unittest.main()
