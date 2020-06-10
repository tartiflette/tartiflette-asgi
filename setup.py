#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from pathlib import Path

from setuptools import setup


def get_version(package: str) -> str:
    """Return package version as listed in `__version__` in `__init__.py`."""
    version = Path(package, "__init__.py").read_text()
    match = re.search("__version__ = ['\"]([^'\"]+)['\"]", version)
    assert match is not None
    return match.group(1)


def get_long_description() -> str:
    with open("README.md", encoding="utf8") as readme:
        with open("CHANGELOG.md", encoding="utf8") as changelog:
            return readme.read() + "\n\n" + changelog.read()


def get_packages(package: str) -> list:
    """Return root package and all sub-packages."""
    return [str(path.parent) for path in Path(package).glob("**/__init__.py")]


setup(
    name="tartiflette-asgi",
    version=get_version("tartiflette_asgi"),
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description="ASGI support for the Tartiflette Python GraphQL engine",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/tartiflette/tartiflette-asgi",
    packages=get_packages("tartiflette_asgi"),
    package_data={"tartiflette_asgi": ["py.typed"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=["starlette==0.13.*", "tartiflette>=1.0,<1.3"],
    python_requires=">=3.6",
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
