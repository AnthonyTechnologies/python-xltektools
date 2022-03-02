#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" conftest.py
Used for pytest directory-specific hook implementations and directory inclusion for imports.
"""
# Imports #
# Standard Libraries #
from typing import Dict
from typing import Tuple

import pytest

# Third-Party Packages #

# Local Packages #


# Definitions #
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


# Functions #
def pytest_runtest_makereport(item, call):
    """Handles reports on incremental test calls which are dependent on the success of previous test calls."""
    if "incremental" in item.keywords:
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test (if parametrize is used in combination with incremental)
            parametrize_index = tuple(item.callspec.indices.values()) if hasattr(item, "callspec") else ()
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the original name of the failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(parametrize_index, test_name)


def pytest_runtest_setup(item):
    """Implements incremental to make test calls in classes dependent on the success of previous test calls."""
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test (if parametrize is used in combination with incremental)
            parametrize_index = tuple(item.callspec.indices.values()) if hasattr(item, "callspec") else ()
            # retrieve the name of the first test function to fail for this class name and index
            test_name = _test_failed_incremental[cls_name].get(parametrize_index, None)
            # if name found, test has failed for the combination of class name & test name
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))
