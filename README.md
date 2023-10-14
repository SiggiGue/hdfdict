# hdfdict helps h5py to dump and load python dictionaries

[![CodeFactor](https://www.codefactor.io/repository/github/siggigue/hdfdict/badge)](https://www.codefactor.io/repository/github/siggigue/hdfdict)

[![Build Status](https://travis-ci.org/SiggiGue/hdfdict.svg?branch=master)](https://travis-ci.org/SiggiGue/hdfdict)

[![Coverage Status](https://coveralls.io/repos/github/SiggiGue/hdfdict/badge.svg?branch=master)](https://coveralls.io/github/SiggiGue/hdfdict?branch=master)

If you have a hierarchical data structure of numpy arrays in a dictionary for example, you can use this tool to save this dictionary into a h5py `File()` or `Group()` and load it again.
This tool just maps the hdf `Groups` to dict `keys` and the `Datset` to dict `values`.
Only types supported by h5py can be used.
The dicitonary-keys need to be strings until now.

A lazy loading option is activated per default. So big h5 files are not loaded at once. Instead a dataset gets only loaded if it is accessed from the LazyHdfDict instance.


## Example

```python
import hdfdict
import numpy as np


d = {
    'a': np.random.randn(10),
    'b': [1, 2, 3],
    'c': 'Hallo',
    'd': np.array(['a', 'b']).astype('S'),
    'e': True,
    'f': (True, False),
}
fname = 'test_hdfdict.h5'
hdfdict.dump(d, fname)
res = hdfdict.load(fname)

print(res)
```

Output:
`
{'a': <HDF5 dataset "a": shape (10,), type "<f8">, 'b': <HDF5 dataset "b": shape (3,), type "<i8">, 'c': <HDF5 dataset "c": shape (), type "|O">, 'd': <HDF5 dataset "d": shape (2,), type "|S1">, 'e': <HDF5 dataset "e": shape (), type "|b1">, 'f': <HDF5 dataset "f": shape (2,), type "|b1">}
`

This are all lazy loding fields in the result `res`.
Just call `res.unlazy()` or `dict(res)` to get all fields loaded.
If you only want to load specific fields, just use item access e.g. `res['a']` so only field 'a' will be loaded from the file.


```python
print(dict(res))`
```

Output:
`
{'a': array([-0.47666824,  0.11787749,  0.51405835, -1.49557787, -0.33617182,
       -0.22381693,  0.25966526,  0.58160661,  0.17019176,  1.3167669 ]), 'b': array([1, 2, 3]), 'c': 'Hallo', 'd': array([b'a', b'b'], dtype='|S1'), 'e': True, 'f': array([ True, False])}
`





## Installation

+ `pip install hdfdict`
+ `poetry install hdfdict`
+ `git clone https://github.com/SiggiGue/hdfdict.git` and `python hdfdict/setup.py install`
