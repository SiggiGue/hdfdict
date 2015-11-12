# -*- coding: utf-8 -*-
import h5py
import yaml
from datetime import datetime
from numpy import string_
from contextlib import contextmanager


TYPEID = '__type__'


@contextmanager
def hdf_file(hdf, **kwargs):
    """Context manager yields h5 file and closes if hdf is str,
    otherwise just yield hdf as is."""
    if isinstance(hdf, str):
        hdf = h5py.File(hdf, **kwargs)
        yield hdf
        hdf.close()
    else:
        yield hdf


def load(hdf, **kwargs):
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

    def _recurse(h, d):
        for k, v in h.items():
            if type(v) == h5py.Group:
                d[k] = {}
                d[k] = _recurse(v, d[k])
            elif isinstance(v, h5py.Dataset):
                value = v.value
                if TYPEID in v.attrs:
                    if v.attrs[TYPEID].astype(str) == 'datetime':
                        if hasattr(value, '__iter__'):
                            value = [datetime.fromtimestamp(
                                ts) for ts in value]
                        else:
                            value = datetime.fromtimestamp(value)

                    if v.attrs[TYPEID].astype(str) == 'yaml':
                        value = yaml.safe_load(value.decode())

                d[k] = value
        return d

    with hdf_file(hdf, **kwargs) as hdf:
        d = {}
        return _recurse(hdf, d)


def dump(d, hdf, **kwargs):
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
            else:
                if isinstance(v, datetime):
                    v = v.timestamp()
                    isdt = True

                if hasattr(v, '__iter__'):
                    if all(isinstance(i, datetime) for i in v):
                        v = [item.timestamp() for item in v]
                        isdt = True

                try:
                    ds = h.create_dataset(name=k, data=v)
                    if isdt:
                        ds.attrs.create(
                            name=TYPEID,
                            data=string_("datetime"))
                except TypeError:
                    # Obviously the data was not serializable. To give it
                    # a last try; serialize it to yaml
                    # and save it to the hdf file:
                    ds = h.create_dataset(
                        name=k,
                        data=string_(yaml.safe_dump(v))
                    )
                    ds.attrs.create(
                        name=TYPEID,
                        data=string_("yaml"))
                    # if this fails again, restructure your data!

    with hdf_file(hdf, **kwargs) as hdf:
        _recurse(d, hdf)
        return hdf
