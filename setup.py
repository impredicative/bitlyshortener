"""Package installation setup."""
import distutils.text_file
from pathlib import Path
from typing import List

from setuptools import find_packages, setup

_DIR = Path(__file__).parent


def parse_requirements(filename: str) -> List[str]:
    """Return requirements from requirements file."""
    # Ref: https://stackoverflow.com/a/42033122/
    return distutils.text_file.TextFile(filename=str(_DIR / filename)).readlines()


setup(
    name="bitlyshortener",
    author="Ouroboros Chrysopoeia",
    author_email="impredicative@users.nomail.github.com",
    version="0.4.1",
    description="High-volume Bitly V4 URL shortener with memory-cache",
    keywords="bitly url shortener",
    long_description=(_DIR / "README.md").read_text().strip(),
    long_description_content_type="text/markdown",
    url="https://github.com/impredicative/bitlyshortener/",
    packages=find_packages(exclude=["scripts"]),
    install_requires=parse_requirements("requirements/install.in"),
    python_requires=">=3.7",
    classifiers=[  # https://pypi.org/classifiers/
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
