#!/bin/bash
rundate=$(date '+%Y%m%d'  --date="1 days ago")
# rundate1=$(date '+%Y-%m-%d' --date="1 days ago")
#rundate="20160809"
#rundate1="2016-08-09"
echo "Downoading static geog data"

data_home="/mnt/disks/wrf-mod/DATA/"
mkdir -p $data_home
cd $data_home || exit

geog_dataset="geog_complete.tar.bz2"
geog_location="http://www2.mmm.ucar.edu/wrf/src/wps_files/$geog_dataset"

wget "$geog_location"

tar jxf $geog_dataset

rm -f $geog_dataset

echo "Downoading static geog data: Completed!"
