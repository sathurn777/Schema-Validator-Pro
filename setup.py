#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Schema Validator Pro - Setup Configuration
A production-ready Schema.org JSON-LD validator and generator for WordPress and beyond.
"""

import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='schema-validator-pro',
    version='1.0.0',
    
    # Package metadata
    description='Production-ready Schema.org JSON-LD validator and generator with 97% test coverage',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # Author information
    author='Schema Validator Pro Contributors',
    author_email='schema-validator-pro@example.com',
    
    # URLs
    url='https://github.com/schema-validator-pro/schema-validator-pro',
    project_urls={
        'Bug Reports': 'https://github.com/schema-validator-pro/schema-validator-pro/issues',
        'Source': 'https://github.com/schema-validator-pro/schema-validator-pro',
        'Documentation': 'https://github.com/schema-validator-pro/schema-validator-pro/blob/main/docs/API_REFERENCE.md',
    },
    
    # License
    license='MIT',
    
    # Package discovery
    packages=find_packages(exclude=['tests', 'tests.*', 'backend.tests', 'backend.tests.*']),
    package_data={
        'backend': ['py.typed'],
    },
    include_package_data=True,
    
    # Python version requirement
    python_requires='>=3.9',
    
    # Dependencies
    install_requires=requirements,
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.4.4',
            'pytest-asyncio>=0.21.1',
            'pytest-cov>=4.1.0',
            'pytest-benchmark>=5.1.0',
            'black>=24.1.1',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
        ],
        'wordpress': [
            'requests>=2.31.0',
        ],
    },
    
    # Entry points for CLI
    entry_points={
        'console_scripts': [
            'schema-validator-pro=backend.main:main',
        ],
    },
    
    # PyPI classifiers
    classifiers=[
        # Development status
        'Development Status :: 5 - Production/Stable',
        
        # Intended audience
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        
        # Topic
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        
        # License
        'License :: OSI Approved :: MIT License',
        
        # Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        
        # Framework
        'Framework :: FastAPI',
        
        # Operating systems
        'Operating System :: OS Independent',
        
        # Typing
        'Typing :: Typed',
    ],
    
    # Keywords for PyPI search
    keywords=[
        'schema.org',
        'json-ld',
        'structured-data',
        'seo',
        'validator',
        'wordpress',
        'fastapi',
        'schema-markup',
        'rich-snippets',
        'semantic-web',
    ],
    
    # Zip safe
    zip_safe=False,
)

