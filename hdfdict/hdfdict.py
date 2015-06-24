# -*- coding: utf-8 -*-
import h5py
import json
from datetime import datetime
from numpy import array
from contextlib import contextmanager

TYPEID = '__type__'


@contextmanager
def hdf_file(hdf):
    """Loads h5 file and closes if hdf is str,
    otherwise just uses uses hdf as fid """
    if isinstance(hdf, str):
        hdf = h5py.File(hdf)
        do_close = True
    else:
        do_close = False
    yield hdf
    if do_close:
        hdf.close()


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
    d = {}

    def _recurse(h, d):
        for k, v in h.items():
            if isinstance(v, h5py.Group):
                d[k] = {}
                d[k] = _recurse(v, d[k])
            elif isinstance(v, h5py.Dataset):
                value = v.value
                if TYPEID in v.attrs:

                    if v.attrs[TYPEID][0].astype(str) == 'datetime':
                        if hasattr(value, '__iter__'):
                            value = [datetime.fromtimestamp(
                                ts) for ts in value]
                        else:
                            value = datetime.fromtimestamp(value)

                    if v.attrs[TYPEID][0].astype(str) == 'json':
                        value = json.loads(value)

                d[k] = value
        return d

    with hdf_file(hdf) as hdf:
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

    def _recurse(d, h):
        for k, v in d.items():
            isdt = None
            if isinstance(v, dict):
                g = h.create_group(k)
                _recurse(v, g)
            if isinstance(v, datetime):
                v = v.timestamp()
                isdt = True
            if (hasattr(v, '__iter__') and all(
                    isinstance(i, datetime) for i in v)):
                v = [item.timestamp() for item in v]
                isdt = True
            try:
                ds = h.create_dataset(name=k, data=v)
                if isdt:
                    ds.attrs.create(
                        name=TYPEID,
                        data=array(["datetime"]).astype('S'))
            except TypeError:
                # Obviously the data was not serializable. To giv it
                # a last try; serialize it to json and save it to the hdf file:
                ds = h.create_dataset(name=k, data=json.dumps(v))
                ds.attrs.create(
                    name=TYPEID,
                    data=array(['json']).astype('S'))
                # if this fails again, restructure your data!

    with hdf_file(hdf) as hdf:
        _recurse(d, hdf)
        return hdf
