from setuptools import setup, find_packages

setup(
    name='nous.migration',
    version='0.3',
    description='Utilities to collect interesting stats about your code.',
    author='Ignas Mikalajunas',
    author_email='ignas@nous.lt',
    url='http://github.com/Ignas/nous.migration/',
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Programming Language :: Python"],
    install_requires=[
        'sqlalchemy',
        'PasteDeploy'
        ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
      entry_points = """\
    [console_scripts]
    migrate = nous.migration:main
    """,
    license="GPL"
)
