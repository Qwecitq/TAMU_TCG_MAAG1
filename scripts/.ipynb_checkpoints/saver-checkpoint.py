#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xarray as xr
from tqdm import tqdm

def chunk_save(dataset, chunk_num):
    # Chunk the dataset along the time dimension
    ckd_ds = dataset.chunk({'time': chunk_num})
    slices = []  # List to store slice objects for each chunk

    # Loop through dimensions and chunks to create slice objects
    for dim, chunks in ckd_ds.chunks.items():
        start = 0  # Initialize start index for the dimension
        for chunk in chunks:
            if start >= ckd_ds.sizes[dim]:  # Break if start index exceeds dimension size
                break
            stop = start + chunk  # Calculate stop index for the chunk
            slices.append(slice(start, stop))  # Create a slice object and add to the list
            start = stop  # Update start index for the next chunk

    return ckd_ds, slices  # Return the chunked dataset and list of slice objects

def save_filenames(prefix, vb, dataset, chunk_num):
    filenames = []  # List to store filenames
    in_data = []  # List to store chunked data

    # Call the chunk_save function to chunk the dataset and get slice objects
    chunked_ds, slices = chunk_save(dataset, chunk_num)
    #print(chunked_ds, slices)

    # Loop through the slice objects to create filenames and extract data chunks
    for slic in tqdm(slices, desc='Processing slices'):
        # Get start and end dates for the chunk from time values
        start_date = str(chunked_ds.isel(time=slic).time.values[0])[:13]
        end_date = str(chunked_ds.isel(time=slic).time.values[-1])[:13]
        _nds = chunked_ds.isel(time=slic)  # Extract data chunk for the slice

        # Generate filename based on prefix, start date, and end date
        filename = f'{prefix}_{start_date}-{end_date}.nc'
        filenames.append(filename)  # Add filename to the list
        in_data.append(_nds)  # Add data chunk to the list
    
    filenames=[x+f'_{ix}' for ix,x in enumerate(filenames)]
    in_data_size = [x.nbytes/1024/1024 for x in in_data]
    print(in_data_size)
    # Define encoding options for saving the data
    enc_dict = {'zlib': True, 'complevel': 1, 'fletcher32': True}
    enc = {i: enc_dict for i in vb}  # Create encoding dictionary

    # Save the data as multiple netCDF files using save_mfdataset
    #t = [x.to_netcdf(fn,encoding=enc) for x,fn in zip(in_data,filenames)]#, filenames, encoding=enc)
    t = xr.save_mfdataset(in_data,filenames,encoding=enc)
    return t  # Return the saved dataset

# Example usage
# Assuming 'ds' is your xarray dataset and 'vb' is a list of variables to encode
# result = save_filenames('prefix', ['variable1', 'variable2'], ds, 100)
