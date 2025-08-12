#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#---------------- CALCULATE WINDSPEED AND SELECT Z500 & Z300 FOR TEMPEST EXTREMES TC DETECTION----------------------#

import uxarray as uxr
import glob
import os
import numpy as np
from simplempi.parfor import parfor 
from datetime import datetime, timedelta

# Define paths
main_save_path = '/glade/work/ktquagra/MAAG_project/datasets/pgw_windspeed_unstruc/'
mesh_grid_path = '/glade/derecho/scratch/knocasio/MAAG_test_runs/MAAG.static.nc'
# data_files = glob.glob('/glade/derecho/scratch/knocasio/MAAG_testrun_outputs/diag.2017-09-*.nc', recursive=True)  #CTRL
data_files = glob.glob('/glade/derecho/scratch/arnunez/MPAS/MPAS/diag.2017-09-*.nc', recursive=True) #Pseudo Global Warming Simulations
# Variables to extract and store
target_variables = ['wind_speed10m', 'z300', 'z500','msl']

# Process only the first file for demonstration
for fx in parfor(range(0,len(data_files))):
    file_path = data_files[fx]
    print(f"Processing file: {file_path}")

    # Open unstructured dataset with mesh
    uxds = uxr.open_mfdataset(mesh_grid_path, file_path)

    # Compute 10-m wind speed from u and v components
    wind_speed = np.sqrt(uxds['u10'] ** 2 + uxds['v10'] ** 2)
    wind_speed = wind_speed.rename('wind_speed10m')

    # Create output dataset and add wind speed
    output_ds = uxr.UxDataset()
    output_ds[target_variables[0]] = wind_speed#.isel(Time=0)

    # Extract geopotential height at 300 hPa and 500 hPa levels
    z_iso = uxds['z_isobaric']
    output_ds[target_variables[1]] = z_iso.sel(z_iso_levels=30000)#.isel(Time=0)
    output_ds[target_variables[2]] = z_iso.sel(z_iso_levels=50000)#.isel(Time=0)
    output_ds[target_variables[3]] = uxds['mslp']
    
    # Prepare output path
    _pth = os.path.splitext(os.path.basename(file_path))
    _use_path = _pth[0][5:24]
    _date_time = datetime.strptime(_use_path, "%Y-%m-%d_%H.%M.%S")
    
    output_file_name = _pth[0] + '_tempext_varbs.nc'
    output_file_path = os.path.join(main_save_path, output_file_name)
    os.makedirs(main_save_path,exist_ok=True)

    # Define compression encoding
    compression = {'zlib': True, 'complevel': 1, 'fletcher32': True}
    encoding = {var: compression for var in target_variables}

    # Write the dataset to a NetCDF file
    output_ds['Time'] = [np.datetime64(_date_time)]
    output_ds = output_ds.rename({'Time':'time','n_face':'ncol'})
    output_ds.to_netcdf(output_file_path, encoding=encoding)

    print(f"Saved processed dataset to: {output_file_path}")
