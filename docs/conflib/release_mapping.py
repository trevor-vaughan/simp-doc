from __future__ import print_function
import sys
import glob
import os
import urllib2
import re
import json
import yaml

from data_merge import *

from IPython import embed

def get_version_map(target_version, basedir, github_api_content_url_base, github_version_targets):
    """
    Fetch the version map

    Local directories are checked first and, if those fail, maps are pulled
    from GitHub directly
    """

    os_ver_mapper_name = 'release_mappings.yaml'

    os_ver_mappers = glob.glob(os.path.join(basedir, '..', '..', '..', 'build', 'distributions', '*', '*', '*', os_ver_mapper_name))

    if not os_ver_mappers:
        os_ver_mappers = glob.glob(os.path.join(basedir, '..', '..', '..', 'build', os_ver_mapper_name))

    if os_ver_mappers:
        ver_map = {}

        for os_ver_mapper in os_ver_mappers:
            with open(os_ver_mapper, 'r') as f:
                ver_map = data_merge(ver_map, yaml.load(f.read()))
    else:
        os_ver_mapper_urls = []

        for version_target in github_version_targets:
            github_version_ref = '?ref=' + version_target

            # Find the directories in GitHub
            for _distro in [
                    item['path'] for item in filter(
                        lambda x: x['type'] == 'dir', json.loads(
                            urllib2.urlopen(github_api_content_url_base + github_version_ref)
                        )
                    )
                ]:

                embed()

            # Grab them from the Internet!
            for os_ver_mapper_url in os_ver_mapper_urls:
                try:
                    print("NOTICE: Downloading Version Mapper: " + os_ver_mapper_url, file=sys.stderr)
                    os_ver_mapper_content = urllib2.urlopen(os_ver_mapper_url).read()
                    # If we don't have a valid version from the RPM spec file, just
                    # pick up what we found.
                    if not target_version or (target_version == '0.0'):
                        version = version_target
                    break
                except urllib2.URLError:
                    next

        #release_mapping_list = ['Release Mapping Entry Not Found for Version ' + full_version]

def format_version_map(ver_map):
    """ Return a version of the version map that is suitable for printing. """

    os_flavors = None

    map_versions = sorted(ver_map['simp_releases'].keys(), reverse=True)

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
