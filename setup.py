"""
Setup script for PROJEK DENGKIS.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]

setup(
    name='projek-dengkis',
    version='0.3.0',
    description='Kali Linux-first security assessment tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PROJEK DENGKIS Team',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'dengkis=cli.main:main',
            'dengkis-gui=gui.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
