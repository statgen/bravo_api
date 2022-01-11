"""BRAVO Data API.

"""

# Always prefer setuptools over distutils
from setuptools import setup
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here/'README.md').read_text(encoding='utf-8')

setup(
    name='bravo-api',
    version='2.1.0',
    description='Browse all variants online data API',

    # Read from README.md
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/statgen/bravo_api',
    author='CSG at University of Michigan',
    author_email='bravo-group@umich.edu',

    # Classification metadata
    classifiers=[
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        # Python versions supported.
        # Not checked by 'pip install'. Use 'python_requires' below.
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='bioinformatics, genomics',  # Optional

    # package_dir={'': '.'},  # Optional
    packages=['bravo_api'],

    # Python versions you support. Pip enforces this.
    python_requires='>=3.8, <4',

    install_requires=[
        'pymongo>=3.11.2', 'click>=7.1.2', 'Flask>=1.1.2', 'flask_compress>=1.9.0',
        'flask_cors>=3.0.10', 'flask_pymongo>=2.3.0', 'intervaltree>=3.1.0', 'marshmallow>=3.10.0',
        'pysam>=0.16.0.1', 'python-rapidjson>=1.0', 'rapidjson>=1.0.0', 'webargs>=7.0.1'
    ],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['mongomock>=3.22.1', 'pytest>=6.2.2', 'pytest-mock==3.5.1',
                 'pytest-mongodb>=2.2.0', 'testfixtures>=6.17.1'],
    },

    entry_points={
        'flask.commands': [
            'load-genes=bravo_api.models.database:load_genes',
            'load-snv=bravo_api.models.database:load_snv',
            'load-qc-metrics=bravo_api.models.database:load_qc_metrics',
            'create-users=bravo_api.models.database.create_users'
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/statgen/bravo_api/issues',
        'Source': 'https://github.com/statgen/bravo_api',
    },
)
