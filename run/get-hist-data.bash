#!/bin/bash

function print_elapsed_time {
	printf '%s - Time elapsed %dh:%dm:%ds\n' "$1" $(($2/3600)) $(($2%3600/60)) $(($2%60))
}

tot_start=$(date +%s)

lib_path="/opt/lib"
wrf_home="/mnt/disks/wrf-mod"

geog_home="$wrf_home/DATA/geog/"
gfs_home="$wrf_home/DATA/GFS/"

src_home="$wrf_home/wrf-scripts/src"
ncl_home="$wrf_home/wrf-scripts/ncl"
log_home="$wrf_home/logs"

if [ -z "$1" ]; then
    rundate=$(date '+%Y%m%d'  --date="0 days ago")
    else
    rundate=$1
fi

log_file="daily.data.$rundate-$(date +"%Y-%m-%d_%H%M").log"

wrf_output="$wrf_home/OUTPUT"
ncl_output="$wrf_output/NCL"

echo "Redirecting logs to $log_home/$log_file"
mkdir -p $log_home
exec > "$log_home/$log_file"


echo "Rundate: $rundate"

mkdir -p $gfs_home

cd $gfs_home || exit

if [ -f runlock.txt ]; then
        echo "get.bash is already running";
        exit;
fi 

datafile="${rundate}.gfs.t00z.pgrb2.0p50.f075"

#echo $datafile
if [ -f "${datafile}" ]; 
        then
        find2=$(find ./ -size 0 | grep "${rundate}")
# echo $find2
if [ ! -e "${find2}"  ]; then
        echo "Data already there";
        exit;
else
        echo "start downloading"
fi
else
        echo "Data not downloaded. Start downloading";
fi

rm -rf ./*

touch runlock.txt

year1=${rundate:0:4}
month1=${rundate:5:2}
date1=${rundate:8:2}
DataLink="ftp://nomads.ncdc.noaa.gov/GFS/Grid4/$year1$month1/$year1$month1$date1/"
echo "$DataLink"

get_data() {
        rundate="$2"
        echo "Downloading data for $rundate"
        DataLink="$3"
        DataName1="gfs_4_${rundate}_0000_0${1}.grb2"
        DataName="gfs.t00z.pgrb2.0p50.f0"$1
        wget "${DataLink}"/"${DataName1}" -O ./"${rundate}"."${DataName}"
 }

export -f get_data

seq -f "%02g $(echo "${rundate//-}") $DataLink" 0 3 75 | xargs -n 1 -P 10 -I {} bash -c 'get_data $@' _ {}

rm runlock.txt

end=$(date +%s)
secs=$((end-tot_start))
print_elapsed_time "Data-download" $secs

exit
