from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in ploy_app/__init__.py
from ploy_app import __version__ as version

setup(
	name='ploy_app',
	version=version,
	description='System usage listing',
	author='Jide Olayinka',
	author_email='spryng.managed@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
