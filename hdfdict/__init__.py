# -- coding: utf-8 --
"""hdfdict helps h5py to dump and load python dictionaries

If you have a hierarchical data structure of numpy arrays in a
dictionary for example, you can use this tool to save this
dictionary into a h5py `File()` or `Group()` and load it again.
This tool just maps the hdf `Groups` to dict `keys` and
the `Datset` to dict `values`.
Only types supported by h5py can be used.
The dicitonary-keys need to be strings until now.

Example
-------

```python
import numpy as np
import hdfdict

d = {
        'testdata': np.random.randn(10),
        'b': np.sin(np.linspace(0, 10))
}

hdf = hdfdict.dump(d, 'test.h5')

res = hdfdict.load(hdf)

print(res)

```


"""

from .hdfdict import load, dump
import pkg_resources as __pkg_resources

__version__ = __pkg_resources.require('hdfdict')[0].version

__all__ = ['load', 'dump']
