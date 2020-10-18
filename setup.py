from setuptools import setup


setup(
    name="tbselenium",
    description="Tor Browser automation with Selenium",
    keywords=["tor", "selenium", "tor browser"],
    version="0.5.1",
    url = 'https://github.com/webfp/tor-browser-selenium',
    packages=["tbselenium", "tbselenium.test"],
    install_requires=[
        "selenium>=3.14"
    ]
)
