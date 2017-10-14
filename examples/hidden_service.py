from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def search_with_ddg_hidden_service(tbb_dir):
    ddg_hs_url = "http://3g2upl4pq6kufc4m.onion"  # DuckDuckGo Hidden Service
    with TorBrowserDriver(tbb_dir) as driver:
        driver.load_url(ddg_hs_url)
        search_box = driver.find_element_by("#search_form_input_homepage")
        search_box.send_keys("Citizenfour")
        search_box.send_keys(Keys.RETURN)
        driver.find_element_by("More at Wikipedia",
                               timeout=60,
                               find_by=By.LINK_TEXT)


def main():
    desc = "Search using DuckDuckGo's hidden service"
    parser = ArgumentParser(description=desc)
    parser.add_argument('tbb_path')
    args = parser.parse_args()
    search_with_ddg_hidden_service(args.tbb_path)


if __name__ == '__main__':
    main()
