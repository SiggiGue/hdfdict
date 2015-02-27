# -- encoding: utf-8 --

from setuptools import setup, find_packages

setup(name='hdfdict',
      version='0.1alpha',
      description='Save dictionaries in HDF-Files.',
      author='Siegfried Guendert',
      author_email='siegfried.guendert@googlemail.com',
      license='MIT',
      keywords='scientific serialize data exchange',
      packages=find_packages(exclude=('docs', '.git')),
      install_requires=['h5py'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ]
)
