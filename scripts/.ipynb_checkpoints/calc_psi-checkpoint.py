#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from xspharm import xspharm
import xarray as xr 
import numpy as np 
import os 
import glob
from dask import delayed
import pathlib
from datetime import datetime, timedelta
from simplempi.parfor import parfor

### Obtain the data dates from original files
base = f"/glade/derecho/scratch/knocasio/MAAG_testrun_outputs/"

#obtain data files 
paths = glob.glob(f"{base}/diag.2017-09-*", recursive=True)
paths.sort()            #sort data files 

# Create numpy datetime for each file's date 
dnames = []
for path in paths:
    _pth = os.path.split(path)
    _use_path = _pth[1][5:24]
    _date_time = datetime.strptime(_use_path, "%Y-%m-%d_%H.%M.%S")
    dnames.append(np.datetime64(_date_time))
    
regridded_path = glob.glob(f"{base}post_process/deg.25_diag.2017-09*.nc")
main_data = delayed(xr.open_mfdataset)(regridded_path, combine='nested', concat_dim='xtime').assign_coords( 
    lon=(lambda ds: (ds.lon + 180) % 360 - 180)).sortby(                       #redefine lon-lats
    lambda ds: ds['lon']).assign_coords(          #sort lon-lat axes
    xtime=dnames).compute()[['umeridional_850hPa','uzonal_850hPa']]


year=2017
month=9

times = main_data.xtime.values[:10]
psi_data = []
for tx in times:
    print(f"\n--- Processing Year {year}, Month {str(month).zfill(2)} ---")

    # Define data path
    # mpaths = f"/global/cfs/cdirs/m4374/input_datasets/year2_E3SM_from_meng_zhang_regridded/e3smv2_default_ne120pg2_2005-2015_regrid/"

    # print(f"Looking for U and V files in: {mpaths}")

    # # Find U and V files
    # main_data = xr.open_mfdataset(f"{mpaths}v2*.h4.{year}-{str(month).zfill(2)}*.nc")[['U850','V850']]
    timesel= tx
    u_data = main_data['uzonal_850hPa'].sel(xtime=timesel).load()
    v_data = main_data['umeridional_850hPa'].sel(xtime=timesel).load()

    # Load U and V datasets and select 850 hPa level
    print("    - Opening U and V data")
    u = u_data#[ix]
    v = v_data#[ix]

    # Initialize xspharm object
    print("    - Creating spherical harmonics object")
    xsp = xspharm(u, gridtype='regular')

    # Compute streamfunction and velocity potential
    print("    - Computing streamfunction and velocity potential")
    sfvp_ds = xsp.uv2sfvp(u, v, ntrunc=24)

    # Keep only streamfunction and rename
    sv_data = sfvp_ds.rename({'sf': 'streamfunction'})[['streamfunction']]
    psi_data.append(sv_data)

    print("    - Streamfunction added to list")


# Output directory
sv_path = '/glade/derecho/scratch/ktquagra/E3SM_psi/'
os.makedirs(sv_path, exist_ok=True)

# Save final output
data_name = f'{sv_path}psi_{year}{str(month).zfill(2)}.nc'
enc_dict = {'zlib': True, 'complevel': 1, 'fletcher32': True}
enc = {"streamfunction": enc_dict}

print(f"\n📦 Saving output to {data_name}")
final_dataset = xr.concat(psi_data, dim='time')
final_dataset.to_netcdf(data_name, encoding=enc)
print("✅ Save complete.\n")


