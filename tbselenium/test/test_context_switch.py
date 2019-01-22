import unittest
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.common import CHECK_TPO_URL

# based on https://stackoverflow.com/a/6549765
ENUMERATE_FONTS = """
var font_enumerator = Components.classes["@mozilla.org/gfx/fontenumerator;1"]
.getService(Components.interfaces.nsIFontEnumerator);
return enumerator.EnumerateAllFonts({});"""

COMPONENT_CLASSES_JS = "var c = Components.classes; return c;"


class TestGeckoDriverChromeScript(unittest.TestCase):

    def test_bundled_font_via_chrome_script(self):
        # do not disable this pref when crawling untrusted sites
        pref_dict = {"dom.ipc.cpows.forbid-unsafe-from-browser": False}

        with TBDriverFixture(TBB_PATH, pref_dict=pref_dict) as driver:
            driver.load_url_ensure(CHECK_TPO_URL)
            driver.set_context('chrome')
            components = driver.execute_script(COMPONENT_CLASSES_JS)
            self.assertIn("@mozilla.org/gfx/fontenumerator",
                          str(components))
            used_fonts = driver.execute_script(ENUMERATE_FONTS)
            self.assertIn("Arimo", str(used_fonts))
