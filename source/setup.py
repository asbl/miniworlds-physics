from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="miniworlds_physics",
    version="2.0.0.1",
    description="Physics engine for miniworlds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["games", "education", "mini-worlds", "pygame"],  # arbitrary keywords
    author="Andreas Siebel",
    author_email="andreas.siebel@it-teaching.de",
    url="https://github.com/asbl/miniworlds",
    download_url="https://github.com/asbl/miniworlds",
    license="OSI Approved :: MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
    ],
    packages=find_packages(
        exclude=["contrib", "docs", "tests", "examples"]
    ),  # Required
    package_dir={"miniworlds_physics": "miniworlds_physics"},
    install_requires=["miniworlds", "pymunk"],
    include_package_data=True,
)
