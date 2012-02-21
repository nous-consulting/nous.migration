import os
from setuptools import setup, find_packages

def get_long_description():
    dirname = os.path.dirname(__file__)
    readme = os.path.join(dirname, 'README.txt')
    f = open(readme, 'rb')
    try:
        return f.read()
    finally:
        f.close()

setup(
    name='nous.migration',
    version='0.7',
    description='Yet another sqlalchemy based database schema migration tool',
    long_description=get_long_description(),
    author='Ignas Mikalajunas',
    author_email='ignas@nous.lt',
    url='http://github.com/nous-consulting/nous.migration/',
    classifiers=["Development Status :: 4 - Beta",
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
    add_migration_script = nous.migration:add_migration_script
    """,
    license="GPL"
)
