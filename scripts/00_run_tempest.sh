#!/bin/bash

# Path to your conda installation (modify this if necessary)
#CONDA_BASE=$(conda info --base)

# Initialize conda
#source "$CONDA_BASE/etc/profile.d/conda.sh"

echo $CONDA_DEFAULT_ENV

# Activate the conda environment
# Path to your conda installation (modify this if necessary)
CONDA_BASE=$(conda info --base)

# Initialize conda
source "$CONDA_BASE/etc/profile.d/conda.sh"
conda activate tempest
echo $CONDA_DEFAULT_ENV


yymm='PGW_2017_09_15_31_test4'
#yymm=202305
in_path='../datasets/'
out_path='../datasets/TE_data_MPAS/'
final_output_path='../datasets/AR_dataset/'
unstruc_grid_mesh='/glade/derecho/scratch/knocasio/MAAG_test_runs/MAAG.init.nc'
mkdir -p $out_path
mkdir -p $final_output_path


#ALL Input file u/home/ktquagra/MAAG_project/datasets/windspeed_unstruc/diag.2017-09-17_00.00.00_tempext_varbs.nc
INPUT_FILE="../mpas_ko_scripts/post_process/ter_deg.25_PGW_TEMPEST_preprocessed_data_2017_09_15-31.nc"
#INPUT_FILE_ARPROB="/pscratch/sd/a/abowden/DOE_LBNL_SUMMER"

echo "$INPUT_FILE"

#Output file 
OUTPUT_FILE=${out_path}
FINAL_OUTPUT_FILE=${final_output_path}
#TECA BARD START
echo "TEMPEST APPLICATION: START"

#test1=170
#test2=200
#test3=120
#test4=100 min_time=12h
#STEP 1: FIND TC AND ITS TRACK
DetectNodes --in_data ${INPUT_FILE} --timefilter '3hr' --out ${OUTPUT_FILE}DN_test_${yymm}.txt --searchbymin msl --closedcontourcmd 'msl,170.0,5.5,0;_DIFF(z300,z500),-58.8,6.5,1.0' --mergedist 6.0 --outputcmd 'msl,min,0;wind_speed10m,max,2' 

#--in_connect $unstruc_grid_mesh


echo "STEP 1.1: FIND TC: DONE"

StitchNodes --in ${OUTPUT_FILE}DN_test_${yymm}.txt --out ${OUTPUT_FILE}SN_test_${yymm}.txt --in_fmt 'lon,lat,slp,wind' --range 8.0 --mintime '24h' --maxgap '24h' --threshold 'wind,>=,10,6;lat,<=,36.25,6;lat,>=,-5.0,6' # --lonname 'longitude' --latname 'latitude'
# echo "STEP 1.2: FIND TC TRACK: DONE"

# echo "STEP 1: FIND TC AND ITS TRACK: DONE"

# #STEP 2: DECTCT ARS
# DetectBlobs --in_data ${INPUT_FILE} --out ${OUTPUT_FILE}TE_AR_detect_${yymm}.nc --timefilter "6hr" --thresholdcmd "_LAPLACIAN{8,10}(ivt),<=,-20000,0" --minabslat 15 --geofiltercmd "area,>=,4e5km2" --lonname "longitude" --latname "latitude"


# echo "STEP 2: DECECT ARS: DONE"

#STEP 3: FILTER OUT TC w/ ITS TRACK (FROM STEP 1) FROM STEP 2
# NodeFileFilter  --in_nodefile ${OUTPUT_FILE}SN_test_${yymm}.txt  --in_fmt "lon,lat,slp,wind,ivt"  --in_data ${OUTPUT_FILE}TE_AR_detect_${yymm}.nc  --out_data ${FINAL_OUTPUT_FILE}AR_TEMPEST_${yymm}.nc  --var "binary_tag"  --bydist 8.0  --invert  --lonname "longitude" --latname "latitude"


