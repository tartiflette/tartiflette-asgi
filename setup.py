import io
import os
from setuptools import find_packages, setup

CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()


setup(
    name="tartiflette-starlette",
    version="0.5.1",
    author="Florimond Manca",
    author_email="florimond.manca@gmail.com",
    description="ASGI support for the Tartiflette Python GraphQL engine",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tartiflette/tartiflette-starlette",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["starlette>=0.12,<0.13", "tartiflette>=0.12,<0.13"],
    extras_require={
        "dev": [
            "uvicorn>=0.7, <0.9",
            "requests",
            "pytest",
            "black",
            "pylint",
            "bumpversion",
            "pyee>=6, <7",
        ]
    },
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
    ],
)
