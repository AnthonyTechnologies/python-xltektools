#!/usr/bin/env python
# -*- encoding: utf-8 -*-
""" setup.py
The setup for this package, only present to use in develop mode.
"""
# Imports #
# Standard Libraries #
import pathlib
from glob import glob
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


# Third-Party Packages #
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# Definitions #
# Functions #
def get_pyproject_as_setup():
    file_path = pathlib.Path(__file__).parent.joinpath("pyproject.toml")
    with file_path.open(mode="rb") as file:
        pyproject = tomllib.load(file)

    package_info = pyproject["tool"]["poetry"]
    setup_info = package_info.copy()

    dependencies = setup_info["dependencies"].copy()
    py_ver = dependencies.pop("python")
    setup_info["python"] = f">={py_ver.lstrip('^')}" if "^" in py_ver else py_ver
    setup_info["requires"] = []
    for package, version in dependencies.items():
        if isinstance(version, dict):
            version = version["version"]

        if "^" in version:
            version = version.lstrip("^")
            setup_info["requires"].append(f"{package}>={version}")
        elif "=" in version or ">" in version or "<" in version:
            setup_info["requires"].append(f"{package}{version}")
        else:
            setup_info["requires"].append(f"{package}={version}")

    dev = setup_info["dev-dependencies"]
    setup_info["extras"] = []
    for package, version in dev.items():
        if isinstance(version, dict):
            version = version["version"]

        if "^" in version:
            version = version.lstrip("^")
            setup_info["extras"].append(f"{package}>={version}")
        elif "=" in version or ">" in version or "<" in version:
            setup_info["extras"].append(f"{package}{version}")
        else:
            setup_info["extras"].append(f"{package}={version}")

    return setup_info


# Main #
setup_info = get_pyproject_as_setup()

setup(
    name=setup_info["name"],
    version=setup_info["version"],
    license=setup_info["license"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    python_requires=setup_info["python"],
    install_requires=setup_info["requires"],
    # extras_require={
    #     "dev": setup_info["extras"],
    # },
)
