# For a fully annotated version of this file and what it does, see
# https://github.com/pypa/sampleproject/blob/master/setup.py

import ast
import io
import re
import os
from setuptools import find_packages, setup

DEPENDENCIES = ["starlette>=0.12.0.b3, <0.13"]
DEV_DEPENDENCIES = [
    "tartiflette",
    "uvicorn>=0.7, <0.8",
    "requests",
    "pytest",
    "black",
    "pylint",
]
EXCLUDE_FROM_PACKAGES = ["contrib", "docs", "tests*"]
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()


def get_version():
    version_file = os.path.join(CURDIR, "tartiflette_starlette", "version.py")
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(version_file, "r", encoding="utf8") as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


setup(
    name="tartiflette-starlette",
    version=get_version(),
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description="Starlette ASGI adapter for Tartiflette",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    zip_safe=False,
    install_requires=DEPENDENCIES,
    extras_require={"dev": DEV_DEPENDENCIES},
    python_requires=">=3.6",
    # license and classifier list:
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
    ],
)
