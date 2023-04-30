"""
setup.py for fish-id

For reference see
https://packaging.python.org/guides/distributing-packages-using-setuptools/
and 
https://github.com/kennethreitz/setup.py
"""

from pathlib import Path
from setuptools import setup, find_packages

NAME = "fish-id"
VERSION = "0.0.1"
DESCRIPTION = "Pipeline for fish detection and identification using machine learning"
LICENSE = "None"
URL = "https://github.com/JamFox/fish-id"
AUTHOR = "Karl-Andreas Turvas, Ilja Serenko"
EMAIL = "github@jamfox.dev"
REQUIRES_PYTHON = ">=3.10.0"
REQUIREMENTS: dict = {
    "core": [
        # "core-requirement",
    ],
    "dev": [
        # "requirement-for-development-purposes-only",
    ],
    "doc": [
        "sphinx",
        "acc-py-sphinx",
    ],
}

# Import the README and use it as the long-description if exists.
HERE = Path(__file__).parent.absolute()
try:
    with (HERE / "README.md").open("rt", encoding="utf-8") as fh:
        LONG_DESCRIPTION = fh.read().strip()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license=LICENSE,
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS["core"],
    extras_require={
        **REQUIREMENTS,
        # The "dev" extra is the union of "test" and "doc", with an option
        # to have explicit development dependencies listed.
        "dev": [req
                for extra in ["dev", "doc"]
                for req in REQUIREMENTS.get(extra, [])],
        # The "all" extra is the union of all requirements.
        "all": [req for reqs in REQUIREMENTS.values() for req in reqs],
    },
)
