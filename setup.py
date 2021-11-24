from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    author='Gunes Acar',
    name="tbselenium",
    description="Tor Browser automation with Selenium",
    keywords=["tor", "selenium", "tor browser"],
    version="0.6.1",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/webfp/tor-browser-selenium',
    packages=["tbselenium", "tbselenium.test"],
    install_requires=[
        "selenium>=4"
    ]
)
