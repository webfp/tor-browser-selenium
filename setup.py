from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    author='Gunes Acar',
    name="tbselenium",
    description="Tor Browser automation with Selenium",
    keywords=["tor", "selenium", "tor browser"],
    version="0.9.0",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/webfp/tor-browser-selenium',
    packages=["tbselenium", "tbselenium.test"],
    install_requires=[
        "selenium>=4"
    ]
)
