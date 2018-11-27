import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
  name='extended-django-redis',
  version='0.22.2',
  packages=find_packages(),
  include_package_data=True,
  install_requires=['Django==2.1.3', 'django-redis==4.9.0', 'pytz==2018.7', 'redis==2.10.6'],
  description='Extends the standard caching backend for Django to have additional redis features',
)
