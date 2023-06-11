from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import time


def search_with_ddg_onion_service(tbb_dir):
    """Search using DuckDuckGo's Onion service"""

    # https://gitlab.torproject.org/tpo/applications/tor-browser/-/issues/40524#note_2744494
    ddg_hs_url = "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/"
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url(ddg_hs_url, wait_for_page_body=True)
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search_form_input_homepage"))
        )
        print(f'Found search box: {search_box}')
        search_box.send_keys("Citizenfour by Laura Poitras")
        search_box.send_keys(Keys.RETURN)
        t0 = time()
        wp_link = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
            (By.XPATH, f'//a[@href="https://en.wikipedia.org/wiki/Citizenfour"]'))
        )
        print(f'Loaded the search results and found the Wikipedia link in {time() - t0} seconds')
        assert "Citizenfour" in wp_link.text


def main():
    desc = "Search using DuckDuckGo's Onion service"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    search_with_ddg_onion_service(args.tbb_path)


if __name__ == '__main__':
    main()
