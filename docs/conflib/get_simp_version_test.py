#!/usr/bin/python

from __future__ import print_function
import sys
import os

from get_simp_version import *
from constants import *

def print_simp_version():
    """ Small test for get_simp_version() """

    simp_version_dict = get_simp_version(
        BASEDIR,
        GITHUB_BASE,
        GITHUB_VERSION_TARGETS,
        ON_RTD
    )

    if simp_version_dict:
        for k in simp_version_dict:
            print(k + ' => ' + simp_version_dict[k], file=sys.stdout)
    else:
        print('Error: No valid SIMP version found', file=sys.stderr)

print_simp_version()
