from setuptools import setup

setup(
    name="fennel_invest_api",
    version="1.0.9.2",
    description="Unofficial Fennel.com Invest API written in Python Requests",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NelsonDane/fennel-invest-api",
    author="Nelson Dane",
    packages=["fennel_invest_api"],
    install_requires=["requests", "python-dotenv"],
)
