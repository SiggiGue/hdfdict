# -*- coding: utf-8 -*-
import h5py


def _check_hdf_file(hdf):
    if isinstance(hdf, str):
        hdf = h5py.File(hdf)
    return hdf


def load(hdf):
    """Returns a dictionary containing the datasets from given hdf file."""
    hdf = _check_hdf_file(hdf)
    d = {}

    def _recurse(h, d):
        for k, v in h.items():
            if isinstance(v, h5py.Group):
                d[k] = {}
                d[k] = _recurse(v, d[k])
            elif isinstance(v, h5py.Dataset):
                d[k] = v.value
        return d

    return _recurse(hdf, d)


def dump(d, hdf):
    """Returns a dictionary containing the datasets from given hdf file."""
    hdf = _check_hdf_file(hdf)

    def _recurse(d, h):
        for k, v in d.items():
            if isinstance(v, dict):
                g = h.create_group(k)
                _recurse(v, g)
            else:
                h.create_dataset(name=k, data=v)
        return h

    return _recurse(d, hdf)
