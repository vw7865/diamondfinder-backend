#!/usr/bin/env python3
"""
DiamondFinder Backend Setup
"""

from setuptools import setup, find_packages
import os

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#') and not line.startswith('--')]

setup(
    name="diamondfinder-backend",
    version="1.0.0",
    description="DiamondFinder Minecraft Ore Generation API",
    author="DiamondFinder Team",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'diamondfinder-server=server_api:main',
        ],
    },
) 