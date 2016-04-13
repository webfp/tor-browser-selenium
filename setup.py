from setuptools import setup


setup(
    name="tbselenium",
    description="Tor Browser automation with Selenium.",
    keywords=["tor", "selenium", "tor browser", "driver"],
    version=1.0,
    packages=["tbselenium"],
    install_requires=[
        "selenium >= 2.45.0"
    ]
)
