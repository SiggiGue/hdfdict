# -- encoding: utf-8 --

from setuptools import setup, find_packages

setup(name='hdfdict',
      version='0.4.1',
      description=''.join(('Helps h5py to load and dump dictionaries ',
                           'containg types supported by h5py.')),
      author='Siegfried Guendert',
      author_email='siegfried.guendert@googlemail.com',
      license='MIT',
      keywords='scientific serialize dictionaries h5py hdf exchange',
      packages=find_packages(exclude=('docs', '.git')),
      classifiers=[
          'Intended Audience :: Science/Research',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ]
)
