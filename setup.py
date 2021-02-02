"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import os.path
import re
import setuptools


def get_long_description():
    with open("README.md", "r") as fh:
        return fh.read()


def get_version():
    with open(os.path.join("opslib", "osm", "__init__.py"), "r") as fh:
        pkg = fh.read()

    LIBAPI = int(re.search(r"""(?m)^LIBAPI\s*=\s*(\d+)""", pkg).group(1))
    LIBPATCH = int(re.search(r"""(?m)^LIBPATCH\s*=\s*(\d+)""", pkg).group(1))
    return f"{LIBAPI}.{LIBPATCH}"


setuptools.setup(
    name="ops-lib-osm",
    version=get_version(),
    author="David García",
    author_email="david.garcia@canonical.com",
    maintainer="Canonical",
    # maintainer_email="",
    description="Common code for Operator Framework Charms in OSM",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/davigar15/ops-lib-osm",
    packages=["opslib.osm"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    keywords="juju charm opslib osm",
    project_urls={
        "Juju": "https://juju.is/",
        "Juju Operator Framework": "https://pypi.org/project/ops/",
    },
    python_requires=">=3.6",
    install_requires=["ops >= 0.8.0"],
)