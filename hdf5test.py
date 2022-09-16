import h5py
import numpy as np
f = h5py.File("mytestfile.hdf5", "w")

dset = f.create_dataset("mydataset.json", (100,), dtype='i')


f = h5py.File('mytestfile.hdf5', 'a')

list(f.keys())

dset = f['mydataset.json']

print(dset.shape)

print(dset.dtype)

dset[...] = np.arange(100)

print(dset[0])

print(dset[10])

print(dset[:])
