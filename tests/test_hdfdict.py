from pytest import assume
import os
from pathlib import Path
import numpy as np
import h5py
import hdfdict
import datetime

# the tests are far from complete, also if coverage looks like that.

d = {
    'a': np.random.randn(10),
    'b': [1, 2, 3],
    'c': 'Hallo',
    'd': np.array(['a', 'b']).astype('S'),
    'e': True,
    'f': (True, False),
}
fname = Path(__file__).parent.absolute()/'test_hdfdict.h5'


def test_dict_to_hdf():
    if os.path.isfile(fname):
        os.unlink(fname)
    hdfdict.dump(d, fname)
    for lazy in [True, False]:
        res = hdfdict.load(fname, lazy=lazy)
        assume(np.all(d['a'] == res['a']))
        assume(isinstance(res['a'], np.ndarray))
        assume(np.all(np.equal(d['b'], res['b'])))
        assume(isinstance(d['b'], list))
        assume(d['c'] == res['c'])
        assume(tuple(d.keys()) == tuple(res.keys()))


def test_dict_to_hdf_with_datetime():
    d = {
        'e': [datetime.datetime.now() for i in range(5)],
        'f': datetime.datetime.now(datetime.timezone.utc),
        'g': [('Hello', 5), (6, 'No HDF but json'), {'foo': True}],
        'h': {'test2': datetime.datetime.now(), 
              'again': ['a', 1], 
              '(1, 2)': (3, 4)}
    }
    if os.path.isfile(fname):
        os.unlink(fname)

    with h5py.File(fname, mode='w') as hf:
        hdfdict.dump(d, hf)
        res = hdfdict.load(hf, lazy=False)

        def equaldt(a, b):
            d = a.astimezone() - b.astimezone()
            return d.total_seconds() == 0.0

        assume(all([equaldt(a, b) for (a, b) in zip(d['e'], res['e'])]))
        assume(equaldt(d['f'], res['f']))
        assume(d['g'][0][0] == 'Hello')
        assume(d['g'][1][0] == 6)
        assume(d.keys() == res.keys())
        assume(isinstance(res['h']['test2'], datetime.datetime))
        assume(res['h']['again'][0]=='a')
        assume(res['h']['again'][1]==1)        

    if os.path.isfile(fname):
        os.unlink(fname)


if __name__ == '__main__':
    import pytest

    pytest.main()
    if os.path.isfile(fname):
        os.unlink(fname)
