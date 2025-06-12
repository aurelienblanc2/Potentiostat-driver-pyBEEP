from setuptools import setup

setup(
    name="pyBEEP",
    version="0.1.0",
    description="Python library for controlling and acquiring data from a custom potentiostat.",
    author="adpisa",
    packages=["src"], 
    install_requires=[
        "minimalmodbus",
        "numpy",
        "matplotlib",
        "pandas"
    ],
)