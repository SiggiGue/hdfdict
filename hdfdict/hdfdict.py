# -*- coding: utf-8 -*-
import h5py


def _check_hdf_file(hdf):
    """Returns h5py File if hdf is string (needs to be a path)."""
    if isinstance(hdf, str):
        hdf = h5py.File(hdf)
    return hdf


def load(hdf):
    """Returns a dictionary containing the
    groups as keys and the datasets as values
    from given hdf file.

    Parameters
    ----------
    hdf : string (path to file) or `h5py.File()` or `h5py.Group()`

    Returns
    -------
    d : dict
        The dictionary containing all groupnames as keys and
        datasets as values.
    """
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
    """Adds keys of given dict as groups and values as datasets
    to the given hdf-file (by string or object) or group object.

    Parameters
    ----------
    d : dict
        The dictionary containing only string keys and
        data values or dicts again.
    hdf : string (path to file) or `h5py.File()` or `h5py.Group()`

    Returns
    -------
    hdf : obj
        `h5py.Group()` or `h5py.File()` instance
    """
    hdf = _check_hdf_file(hdf)

    def _recurse(d, h):
        for k, v in d.items():
            if isinstance(v, dict):
                g = h.create_group(k)
                _recurse(v, g)
            else:
                h.create_dataset(name=k, data=v)

    _recurse(d, hdf)
    return hdf
