# -*- coding: utf-8 -*-
import h5py
import json
from datetime import datetime
from numpy import array, string_

TYPEID = '__type__'


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
                value = v.value
                if TYPEID in v.attrs:

                    if v.attrs[TYPEID][0].astype(str) == 'datetime':
                        if hasattr(value, '__iter__'):
                            value = [datetime.fromtimestamp(
                                ts) for ts in value]
                        else:
                            value = datetime.fromtimestamp(value)
                    if v.attrs[TYPEID][0].astype(str) == 'string':
                        if not isinstance(value, bytes):
                            value = [ts.decode() for ts in value]
                        else:
                            value = value.decode()
                    if v.attrs[TYPEID][0].astype(str) == 'json':
                        value = json.loads(value.decode())

                d[k] = value
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
            isdt = None
            isstr = None
            if isinstance(v, dict):
                g = h.create_group(k)
                return _recurse(v, g)
            if isinstance(v, datetime):
                v = v.timestamp()
                isdt = True
            if isinstance(v, str):
                v = string_(v)
                isstr = True
            if hasattr(v, '__iter__'):
                if all(isinstance(i, datetime) for i in v):
                    print(all(isinstance(i, datetime) for i in v))
                    v = [item.timestamp() for item in v]
                    isdt = True
                if all(isinstance(i, str) for i in v):
                    v = [string_(item) for item in v]
                    isstr = True
            try:
                ds = h.create_dataset(name=k, data=v)
                if isdt:
                    ds.attrs.create(
                        name=TYPEID,
                        data=array(["datetime"]).astype('S'))
                if isstr:
                    ds.attrs.create(
                        name=TYPEID,
                        data=array(["string"]).astype('S'))
            except TypeError:
                # Obviously the data was not serializable. To give it
                # a last try; serialize it to json and save it to the hdf file:
                ds = h.create_dataset(name=k, data=string_(json.dumps(v)))
                ds.attrs.create(
                    name=TYPEID,
                    data=array(['json']).astype('S'))
                # if this fails again, restructure your data!

    _recurse(d, hdf)
    return hdf
