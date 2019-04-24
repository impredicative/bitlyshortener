from pathlib import Path
from typing import List

from setuptools import setup, find_packages


def parse_requirements(filename: str) -> List[str]:
    """Return requirements from requirements file."""
    # Ref: https://stackoverflow.com/a/42033122/
    requirements = (Path(__file__).parent / filename).read_text().strip().split('\n')
    requirements = [r.strip() for r in requirements]
    requirements = [r for r in sorted(requirements) if r and not r.startswith('#')]
    return requirements


setup(
    name='bitlyshortener',
    author='Ouroboros Chrysopoeia',
    author_email='impredicative@users.nomail.github.com',
    version='0.2.2',
    description='High-volume Bitly V4 URL shortener with memory-cache',
    keywords='bitly url shortener',
    long_description=Path(__file__).with_name('README.md').read_text().strip(),
    long_description_content_type='text/markdown',
    url='https://github.com/impredicative/bitlyshortener/',
    packages=find_packages(exclude=['scripts']),
    install_requires=parse_requirements('requirements/install.in'),
    python_requires='>=3.7',
    classifiers=[  # https://pypi.org/classifiers/
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
