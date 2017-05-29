from __future__ import print_function
import sys
import glob
import os
import urllib2
import re
import base64
import json
import yaml

#from data_merge import *

from deepmerge import Merger
from IPython import embed

def get_version_map(target_version, basedir, github_version_targets, on_rtd):
    """
    Fetch the version map

    Local directories are checked first and, if those fail, maps are pulled
    from GitHub directly
    """

    ver_map = {}

    ver_map_merger = Merger(
        [
            (list, ['append']),
            (dict, ['merge'])
        ],
        ['override'],
        ['override']
        )

    ver_mapper_name = 'release_mappings.yaml'

    if not on_rtd:

        os_ver_mappers = glob.glob(os.path.join(basedir, '..', '..', '..', 'build', 'distributions', '*', '*', '*', ver_mapper_name))

        if not os_ver_mappers:
            os_ver_mappers = glob.glob(os.path.join(basedir, '..', '..', '..', 'build', ver_mapper_name))

        if os_ver_mappers:
            for os_ver_mapper in os_ver_mappers:
                with open(os_ver_mapper, 'r') as f:
                    ver_map_merger.merge(ver_map, yaml.load(f.read()))

    if on_rtd or not ver_map:
        github_api_base = 'https://api.github.com/repos/simp/simp-core/git/trees/'

        for version_target in github_version_targets:
            github_api_target = github_api_base + version_target
            github_opts = '?recursive=1'

            if ver_map:
                break

            try:
                # Grab the distribution tree
                distro_json = json.load(urllib2.urlopen(github_api_target + github_opts))

                release_mapping_targets = [x for x in distro_json['tree'] if (
                    x['path'] and re.search(r'release_mappings.yaml$', x['path'])
                )]

                for release_mapping_target in release_mapping_targets:
                    print("NOTICE: Downloading Version Mapper: " + release_mapping_target['path'], file=sys.stderr)

                    try:
                        release_obj = json.load(urllib2.urlopen(release_mapping_target['url']))

                        release_yaml = base64.b64decode(release_obj['content'])

                        ver_map_merger.merge(ver_map, yaml.load(release_yaml))

                    except urllib2.URLError:
                        print('Error downloading ' + release_mapping_target['path'],  file=sys.stderr)
                        next

            except urllib2.URLError:
                print('Error downloading ' + github_api_target + github_opts, file=sys.stderr)
                next

        return ver_map

def format_version_map(ver_map, on_rtd):
    """ Return a version of the version map that is suitable for printing. """

    os_flavors = None

    map_versions = sorted(ver_map['simp_releases'].keys(), reverse=True)

    release_mapping_list = ['Release Mapping Entry Not Found for Version ' + full_version]

    unstable_releases = []
    for map_version in map_versions:
        if re.search('\.X$', map_version):
            unstable_releases.append(map_version)

    unstable_releases = sorted(unstable_releases, reverse=True)

    major_releases = []
    for head_release in unstable_releases:
        major_version = head_release.split('.')[0]
        if re.search('^' + major_version + '\.', head_release):
            major_releases.append(major_version)

    head_releases = []
    major_found = []
    for map_version in map_versions:
        major_version = map_version.split('.')[0]
        if major_version in major_found:
            continue

        if re.search('^' + major_version + '\.', map_version):
            head_releases.append(map_version)
            major_found.append(major_version)

    # Smash the current release onto the front of the list
    all_releases = head_releases + unstable_releases

    # If we don't have the full version, don't just drop in an empty key
    if full_version in all_releases:
        all_releases.remove(full_version)
        all_releases.insert(0, full_version)

    # Build the Release mapping table for insertion into the docs
    release_mapping_list = []
    for release in all_releases:
        os_flavors = ver_map['simp_releases'][release]['flavors']
        release_mapping_list.append('* **SIMP ' + release + '**')

        # Extract the actual OS version supported for placement in the docs
        if os_flavors is not None:
            if os_flavors['RedHat']:
                ver_list = os_flavors['RedHat']['os_version'].split('.')
                el_major_version = ver_list[0]
                el_minor_version = ver_list[1]
            elif os_flavors['CentOS']:
                ver_list = os_flavors['CentOS']['os_version'].split('.')
                el_major_version = ver_list[0]
                el_minor_version = ver_list[1]

            for os_flavor in os_flavors:
                release_mapping_list.append("\n    * **" + os_flavor + ' ' + os_flavors[os_flavor]['os_version'] + '**')
                for i, iso in enumerate(os_flavors[os_flavor]['isos']):
                    release_mapping_list.append("\n      * **ISO #" + str(i+1) + ":** " + iso['name'])
                    release_mapping_list.append("      * **Checksum:** " + iso['checksum'])

                    # does it match my version?
                    if (not on_rtd) and (release == full_version):
                        saved_major_version = el_major_version
                        saved_minor_version = el_minor_version

                    if (on_rtd) and (release == full_version):
                        saved_major_version = el_major_version
                        saved_minor_version = el_minor_version

        # Trailing newline
        release_mapping_list.append('')

        return release_mapping_list
