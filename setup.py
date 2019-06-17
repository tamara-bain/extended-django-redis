import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
  name='extended-django-redis',
  version='0.23.8',
  packages=find_packages(),
  include_package_data=True,
  install_requires=['Django', 'django-redis==4.9.0', 'pytz', 'redis==2.10.6'],
  description='Extends the standard caching backend for Django to have additional redis features',
)
