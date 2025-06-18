"""BRAVO Data API.
"""

# Always prefer setuptools over distutils
import setuptools
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here/'README.md').read_text(encoding='utf-8')
# Single source of pacakge version from VERSION file
version_text = (here/'bravo_api'/'VERSION').read_text(encoding='utf-8').strip()

setuptools.setup(
    name='bravo-api',
    version=version_text,
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
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='bioinformatics, genomics',

    package_dir={'': '.'},
    packages=setuptools.find_packages(),
    package_data={"bravo_api": ["VERSION"]},

    # Python versions you support. Pip enforces this.
    python_requires='>=3.13, <4',

    install_requires=[
        'authlib>=1.6.0', 'boto3>=1.38', 'cachelib==0.9.0', 'click>=8.2.1', 'Flask>=3.1.1',
        'Flask-Caching>=2.3.1', 'flask_cors>=6.0.1', 'flask-login>=0.6.3', 'flask_pymongo>=3.0.1',
        'intervaltree>=3.1.0', 'marshmallow>=4.0.0', 'pymongo>=4.13.0', 'pysam>=0.23.3',
        'python-rapidjson>=1.20',  'requests>=2.32.4', 'webargs>=8.7.0',
    ],

    extras_require={
        'dev': ['check-manifest', 'icecream'],
        'test': ['mongomock>=3.22.1', 'pytest>=8.4.1', 'pytest-mock>=3.14.1', 'py>=1.11.0',
                 'pytest-mongodb>=2.2.0', 'testfixtures>=6.17.1', 'moto>=5.0.0'],
    },

    entry_points={
        'flask.commands': [
            'load-genes=bravo_api.models.database:load_genes',
            'load-snv=bravo_api.models.database:load_snv',
            'load-qc-metrics=bravo_api.models.database:load_qc_metrics',
            'create-users=bravo_api.models.database:create_users'
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/statgen/bravo_api/issues',
        'Source': 'https://github.com/statgen/bravo_api',
    }
)
