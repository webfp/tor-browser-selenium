from setuptools import setup


setup(
    name="tbselenium",
    description="Tor Browser automation with Selenium",
    keywords=["tor", "selenium", "tor browser"],
    version=0.1,
    url = 'https://github.com/webfp/tor-browser-selenium',
    packages=["tbselenium"],
    install_requires=[
        "selenium>=2.45.0,<3"
    ]
)
