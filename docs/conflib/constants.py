# A list of constants used throughout the code and for testing

import os

BASEDIR = os.path.abspath(os.getcwd())

ON_RTD = os.environ.get('READTHEDOCS') == 'True'

GITHUB_BASE = os.getenv('SIMP_GITHUB_BASE', 'https://raw.githubusercontent.com/simp')

GITHUB_API_CONTENT_URL_BASE = 'https://api.github.com/repos/simp/simp-core/contents/build/distributions'

# This ordering matches our usual default fallback branch scheme
GITHUB_VERSION_TARGETS = [
    'master',
    '5.1.X',
    '4.2.X'
]

CHANGELOG_NAME = 'Changelog.rst'

CHANGELOG = os.getenv('SIMP_CHANGELOG_PATH',
                      os.path.join(BASEDIR, '..', '..', '..', CHANGELOG_NAME)
                     )
