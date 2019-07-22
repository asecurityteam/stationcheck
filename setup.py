'''Setup script for pypi publication'''
import setuptools

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setuptools.setup(
    name='stationcheck',
    version='1.2',
    scripts=['stationcheck', 'pkg/scripts/verify_package_installers'],
    author="aslape",
    author_email="aslape@atlassian.com",
    description="A configurable workstation checker",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/aslape/station-check",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
