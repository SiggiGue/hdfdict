# -*- coding: utf-8 -*-
import h5py
import yaml
from collections import UserDict
from datetime import datetime
from numpy import string_
from contextlib import contextmanager


TYPEID = '__type__'


@contextmanager
def hdf_file(hdf, lazy=True, *args, **kwargs):
    """Context manager yields h5 file if hdf is str,
    otherwise just yield hdf as is."""
    if isinstance(hdf, str):
        if not lazy:
            with h5py.File(hdf, *args, **kwargs) as hdf:
                yield hdf
        else:
            yield h5py.File(hdf, *args, **kwargs)
    else:
        yield hdf


def unpack_dataset(item):
    """Reconstruct a hdfdict dataset.
    Only some special unpacking for yaml and datetime types.

    Parameters
    ----------
    item : h5py.Dataset

    Returns
    -------
    value : Unpacked Data
    
    """
    value = item.value
    if TYPEID in item.attrs:
        if item.attrs[TYPEID].astype(str) == 'datetime':
            if hasattr(value, '__iter__'):
                value = [datetime.fromtimestamp(
                    ts) for ts in value]
            else:
                value = datetime.fromtimestamp(value)

        if item.attrs[TYPEID].astype(str) == 'yaml':
            value = yaml.safe_load(value.decode())
    return value


class LazyHdfDict(UserDict):
    """Helps loading data only if values from the dict are requested.

    This is done by reimplementing the __getitem__ method.

    """
    def __init__(self, _h5file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._h5file = _h5file  # used to close the file on deletion.

    def __getitem__(self, key):
        """Returns item and loads dataset if needed."""
        item = super().__getitem__(key)
        if isinstance(item, h5py.Dataset):
            item = unpack_dataset(item)
            self.__setitem__(key, item)
        return item

    def unlazy(self):
        """Unpacks all datasets.
        You can call dict(this_instance) then to get a real dict.
        """
        load(self, lazy=False)

    def close(self):
        """Closes the h5file if provided at initialization."""
        if self._h5file and hasattr(self._h5file, 'close'):
            self._h5file.close()      

    def __del__(self):
        self.close()

    def _ipython_key_completions_(self):
        """Returns a tuple of keys. 
        Special Method for ipython to get key completion
        """
        return tuple(self.keys())
            

def load(hdf, lazy=True, unpacker=unpack_dataset, *args, **kwargs):
    """Returns a dictionary containing the
    groups as keys and the datasets as values
    from given hdf file.

    Parameters
    ----------
    hdf : string (path to file) or `h5py.File()` or `h5py.Group()`
    lazy : bool
        If True, the datasets are lazy loaded at the moment an item is requested.
    upacker : callable
        Unpack function gets `value` of type h5py.Dataset.
        Must return the data you would like to have it in the returned dict.

    Returns
    -------
    d : dict
        The dictionary containing all groupnames as keys and
        datasets as values.
    """

    def _recurse(hdfobject, datadict):
        for key, value in hdfobject.items():
            if type(value) == h5py.Group or isinstance(value, LazyHdfDict):
                if lazy:
                    datadict[key] = LazyHdfDict()
                else:
                    datadict[key] = {}
                datadict[key] = _recurse(value, datadict[key])
            elif isinstance(value, h5py.Dataset):
                if not lazy:
                    value = unpacker(value)
                datadict[key] = value

        return datadict

    with hdf_file(hdf, lazy=lazy, *args, **kwargs) as hdf:
        if lazy:
            data = LazyHdfDict(_h5file=hdf)
        else:
            data = {}
        return _recurse(hdf, data)


def pack_dataset(hdfobject, key, value):
    """Packs a given key value pair into a dataset in the given hdfobject."""
    isdt = None
    if isinstance(value, datetime):
        value = value.timestamp()
        isdt = True

    if hasattr(value, '__iter__'):
        if all(isinstance(i, datetime) for i in value):
            value = [item.timestamp() for item in value]
            isdt = True

    try:
        ds = hdfobject.create_dataset(name=key, data=value)
        if isdt:
            ds.attrs.create(
                name=TYPEID,
                data=string_("datetime"))
    except TypeError:
        # Obviously the data was not serializable. To give it
        # a last try; serialize it to yaml
        # and save it to the hdf file:
        ds = hdfobject.create_dataset(
            name=key,
            data=string_(yaml.safe_dump(value))
        )
        ds.attrs.create(
            name=TYPEID,
            data=string_("yaml"))
        # if this fails again, restructure your data!   


def dump(data, hdf, packer=pack_dataset, *args, **kwargs):
    """Adds keys of given dict as groups and values as datasets
    to the given hdf-file (by string or object) or group object.

    Parameters
    ----------
    data : dict
        The dictionary containing only string keys and
        data values or dicts again.
    hdf : string (path to file) or `h5py.File()` or `h5py.Group()`
    packer : callable
        Callable gets `hdfobject, key, value` as input.
        `hdfobject` is considered to be either a h5py.File or a h5py.Group.
        `key` is the name of the dataset.
        `value` is the dataset to be packed and accepted by h5py.

    Returns
    -------
    hdf : obj
        `h5py.Group()` or `h5py.File()` instance

    """

    def _recurse(datadict, hdfobject):
        for key, value in datadict.items():
            if isinstance(key, tuple):
                key = '_'.join((str(i) for i in key))
            if isinstance(value, (dict, LazyHdfDict)):
                hdfgroup = hdfobject.create_group(key)
                _recurse(value, hdfgroup)
            else:
                packer(hdfobject, key, value)

    with hdf_file(hdf, *args, **kwargs) as hdf:
        _recurse(data, hdf)
        return hdf
