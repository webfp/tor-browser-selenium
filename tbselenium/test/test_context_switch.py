import unittest
from tbselenium.test import TBB_PATH
from tbselenium.test.fixtures import TBDriverFixture
from tbselenium.common import USE_RUNNING_TOR, CHECK_TPO_URL

GET_USED_FONT_FACES_JS = """var curWin = document.commandDispatcher.focusedWindow;
        if (curWin.gBrowser && curWin.gBrowser.contentDocumentAsCPOW) {
            curWin = curWin.gBrowser.contentDocumentAsCPOW.defaultView
        }
    var gDocument = document;
    var range = gDocument.createRange();
    range.selectNode(gDocument.documentElement);
    var domUtils =
      Components.classes["@mozilla.org/inspector/dom-utils;1"]
        .getService(Components.interfaces.inIDOMUtils);
    var fonts = domUtils.getUsedFontFaces(range);

    var len = fonts.length;
    var list = [];
    for (var i = 0; i < len; ++i) {
      list.push(fonts.item(i));
    }
    return list;"""

COMPONENT_CLASSES_JS = "var c = Components.classes; return c;"


class TestGeckoDriverChromeScript(unittest.TestCase):

    def test_bundled_font_via_chrome_script(self):
            # do not disable this pref when crawling untrusted sites
            pref_dict = {"dom.ipc.cpows.forbid-unsafe-from-browser": False}

            with TBDriverFixture(TBB_PATH, pref_dict=pref_dict) as driver:
                driver.load_url_ensure(CHECK_TPO_URL)
                driver.set_context('chrome')
                components = driver.execute_script(COMPONENT_CLASSES_JS)
                self.assertIn("mozilla.org/inspector/dom-utils",
                              str(components))
                used_fonts = driver.execute_script(GET_USED_FONT_FACES_JS)
                self.assertIn("Arimo", str(used_fonts))
