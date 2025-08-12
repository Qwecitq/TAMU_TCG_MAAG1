# THINGS TO DO TO RUN THE TEMPEST TRACKER ON MAAG SIMULATIONS 
### NOTE THAT WE START THIS PROCESS ON THE UNSTRUCTURED GRIDS AND RECONVERT BACK TO THE STRUCTURED GRIDS 

* Obtain the path to the simulations:
  - main_save_path = '/glade/work/ktquagra/MAAG_project/datasets/pgw_windspeed_unstruc/'
  - mesh_grid_path = '/glade/derecho/scratch/knocasio/MAAG_test_runs/MAAG.static.nc'
  - data_files = '/glade/derecho/scratch/arnunez/MPAS/MPAS/diag.2017-09-*.nc'
 
* Reconstruct the data and select the required variables for detecting TCs using TempestExtremes
  - variable (name_structure) MSL (msl), 10m windspeed (windspeed10m), geopotential at 300 and 500 (z300,z500)
  - Apply the script `calc_windspeeds.py`. Make sure to edit this with the required paths
  - Run the pbs script (`02_calc_ws.pbs`). Use `qsub 02_calc_ws.pbs` on the NCAR system. 
 
* Merge the reconstructed hourly data into one file to be changed from the unstructured grid to the ERA5-like grid.
  - You can use cdo or just xarray mfdateset to open them together and store them as one file
 
* Regrid merged data into the structured grids.
  - Use the script in the directory `mpas_ko_scripts/remap_latlon_one_file.pbs` to regrid to the structured grid
  - Make sure to change the directory (infile) to the path where you have your merged data.

* If you do not have Tempest Tracker installed in conda, you can check it out here: `https://anaconda.org/conda-forge/tempest-extremes`
* You can run the tempest tracker using the `00_run_tempest.sh`.
  - This simulation is relatively short and not computationally intensive, so you can run it using just your JupyterLab terminal.

You finally have the TCs tracked in the SN_*** file. Cheers! 