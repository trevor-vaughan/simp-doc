#!/usr/bin/python

from __future__ import print_function
import sys

from release_mapping import *
from constants import *

def print_release_mapping():
    """ Small test for get_simp_version() """

    release_mapping_dict = get_version_map(
        '0.0',
        BASEDIR,
        GITHUB_API_CONTENT_URL_BASE,
        GITHUB_VERSION_TARGETS,
        ON_RTD
    )

    if release_mapping_dict:
        for k in release_mapping_dict:
            print(k + ' => ' + release_mapping_dict[k], file=sys.stdout)
    else:
        print('Error: No valid release mappings found', file=sys.stderr)

print_release_mapping()
