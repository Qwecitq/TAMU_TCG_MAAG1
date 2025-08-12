#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xarray as xr
import numpy as np
from simplempi.parfor import parfor
import os
import glob
from tqdm import tqdm
from dask import delayed
from dask.diagnostics import ProgressBar
from metpy.calc import dewpoint_from_specific_humidity, equivalent_potential_temperature
from metpy.units import units
from datetime import datetime  # Use datetime from standard library

# Enable Dask progress bar for better visualization of compute steps
ProgressBar().register()

# Paths for ERA5 data and where to save processed output
era5_path = "/glade/campaign/collections/rda/data/d633000/e5.oper.an.pl/"
main_save_path = '/glade/work/ktquagra/MAAG_project/datasets/'

year = 2017
months = np.arange(9, 10)  # Process September to October

for mm in months:
    # -------------------------------
    # 1. Load TEMPERATURE ('t') data
    # -------------------------------
    var = 't'
    dpath_t = glob.glob(f'{era5_path}{year}{str(mm).zfill(2)}/*_{var}.*.nc')
    dpath_t.sort()
    var = 'q'
    dpath_q = glob.glob(f'{era5_path}{year}{str(mm).zfill(2)}/*_{var}.*.nc')
    dpath_q.sort()
    
    for dpt,(ix,dpq) in zip(dpath_t,enumerate(dpath_q)):
        var = 't'
        _ds_t = delayed(xr.open_mfdataset)(dpt).assign_coords(
            longitude=lambda ds: (ds.longitude + 180) % 360 - 180  # Convert to [-180, 180]
        ).sortby(
            lambda ds: ds['longitude']
        )[var.upper()].compute().load().transpose('time', ..., 'level')
    
        # -------------------------------
        # 2. Load SPECIFIC HUMIDITY ('q') data
        # -------------------------------
        
        var = 'q'
        _ds_q = delayed(xr.open_mfdataset)(dpq).assign_coords(
            longitude=lambda ds: (ds.longitude + 180) % 360 - 180
        ).sortby(
            lambda ds: ds['longitude']
        )[var.upper()].compute().load().transpose('time', ..., 'level')
    
        # -------------------------------
        # 3. Compute Dew Point Temperature
        # -------------------------------
        _pressure = _ds_q.level.values  # Pressure levels in hPa
    
        # MetPy expects quantities with units
        _ds_DewPoint = dewpoint_from_specific_humidity(
            _pressure * units.hPa,
            _ds_q * units('kg/kg')
        )
    
        # -------------------------------
        # 4. Compute Equivalent Potential Temperature (θe)
        # -------------------------------
        _ds_theta_e = equivalent_potential_temperature(
            _pressure * units.hPa,
            _ds_t.transpose('time', ..., 'level') * units.K,
            _ds_DewPoint
        )
    
        # Convert to xarray datasets
        ds_theta_e = _ds_theta_e.to_dataset(name='theta_e')
        ds_DewPoint = _ds_DewPoint.to_dataset(name='dewpoint')
    
        # ===============================
        # 5. Save Equivalent Potential Temperature
        # ===============================
        sv_path_theta = 'Theta/'
        os.makedirs(f"{main_save_path}{sv_path_theta}", exist_ok=True)
        final_sv_path_theta_e = f'{main_save_path}{sv_path_theta}era5_theta_e_{year}{str(mm).zfill(2)}{str(ix+1).zfill(2)}.nc'
    
        enc_dict = {'zlib': True, 'complevel': 7, 'fletcher32': True}
        enc_theta = {"theta_e": enc_dict}
    
        # Add global attributes
        ds_theta_e.attrs.update({
            "description": "Equivalent Potential Temperature calculated from ERA5 using MetPy",
            "source_data": "ECMWF Reanalysis version 5",
            "version": "1.0.1",
            "created_by": "Kwesi T. Quagraine [https://orcid.org/0000-0002-6452-1847]",
            "Date": str(datetime.now())
        })
        ds_theta_e["theta_e"].attrs.update({
            "units": "K",
            "long_name": "Equivalent Potential Temperature",
            "standard_name": "equivalent_potential_temperature"
        })
    
        # Save θe dataset
        ds_theta_e.to_netcdf(final_sv_path_theta_e, encoding=enc_theta)
    
        # ===============================
        # 6. Save Dew Point Temperature
        # ===============================
        sv_path_dew = 'Dewpoint_Temperature/'
        os.makedirs(f"{main_save_path}{sv_path_dew}", exist_ok=True)
        final_sv_path_dew = f'{main_save_path}{sv_path_dew}era5_dewpoint_{year}{str(mm).zfill(2)}{str(ix+1).zfill(2)}.nc'
    
        enc_dewpoint = {"dewpoint": enc_dict}
    
        ds_DewPoint.attrs.update({
            "description": "Dewpoint Temperature calculated from ERA5 using MetPy",
            "source_data": "ECMWF Reanalysis version 5",
            "version": "1.0.1",
            "created_by": "Kwesi T. Quagraine [https://orcid.org/0000-0002-6452-1847]",
            "Date": str(datetime.now())
        })
        ds_DewPoint["dewpoint"].attrs.update({
            "units": "K",  # MetPy returns dewpoint in Kelvin by default
            "long_name": "Dewpoint Temperature",
            "standard_name": "dew_point_temperature"
        })
    
        # Save dewpoint dataset
        ds_DewPoint.to_netcdf(final_sv_path_dew, encoding=enc_dewpoint)
