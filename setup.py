"""setup.py"""
from setuptools import setup

setup(
    name='hothouse',
    version='0.0.1',
    description='Description',
    author='r1yk',
    license='MIT',
    install_requires=[
        'SQLAlchemy>=1.4.31',
        'pg8000>=1.24.0',
        'python-dotenv>=0.19.2'
    ],
    packages=['hothouse', 'hothouse.postgres'],
    package_dir={'hothouse': 'hothouse',
                 'hothouse.postgres': 'hothouse/postgres'}
)
