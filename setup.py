import os
from setuptools import setup, find_packages
import glob

VERSION = "0.0.1"

src_dir = os.path.dirname(__file__)

install_requires = [
    "boto3>=1.3.1,<1.5.0",
]


def read(filename):
    full_path = os.path.join(src_dir, filename)
    with open(full_path) as fd:
        return fd.read()


if __name__ == "__main__":
    setup(
        name="cloudsns",
        version=VERSION,
        author="Tom Taubkin",
        author_email="tomtaubkin@gmail.com",
        license="New BSD license",
        url="https://github.com/remind101/cloudsns",
        description="Listener for cloudformation events",
        packages=find_packages(),
        install_requires=install_requires,
    )
