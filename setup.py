from setuptools import setup, find_packages

with open('README.rst', 'r') as read_me:
    long_description = read_me.read()

setup(
    name='dltn_checker',
    description='a simple utility to check and harvest metadata records from an OAI request when they meet the'
    'DLTN requirements',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    version="0.0.2",
    author="Mark Baggett",
    author_email="mbagget1@utk.edu",
    maintainer_email="mbagget1@utk.edu",
    url="https://github.com/DigitalLibraryofTennessee/check_and_harvest",
    packages=find_packages(),
    install_requires=["requests>=2.21.0", "xmltodict>=0.12.0", "lxml>=4.3.1", "repox>=0.0.2", "pyyaml>=4.2b1"],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    keywords=["libraries", "dpla", "dltn", "oaipmh", "aggregators"],
)
