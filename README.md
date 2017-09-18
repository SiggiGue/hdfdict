# hdfdict helps h5py to dump and load python dictionaries

If you have a hierarchical data structure of numpy arrays in a dictionary for example, you can use this tool to save this dictionary into a h5py `File()` or `Group()` and load it again.
This tool just maps the hdf `Groups` to dict `keys` and the `Datset` to dict `values`.
Only types supported by h5py can be used.
The dicitonary-keys need to be strings until now.

A lazy loading option is activated per default. So big h5 files are not loaded at once. Instead a dataset gets only loaded if it is accessed from the LazyHdfDict instance.


## Installation

+ `pip install git+https://github.com/SiggiGue/hdfdict.git`
+ `git clone ...` and `python setup.py install`
