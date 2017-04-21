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

DataLink="ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.${rundate}00"
# DN=0
echo "$DataLink"
# while [ $DN -le 75 ]; do
#       DataName="gfs.t00z.pgrb2.0p50.f0"$(printf "%02d" ${DN})

#       if [ -f "${rundate}"."${DataName}" ]; then
#               echo "File $DataName already exists"
#       else 
#               echo "Downloading $DataName"
#               wget "${DataLink}"/"${DataName}" -O ./"${rundate}"."${DataName}"
#       fi

#       find3=$(find ./ -size 0 | grep "${rundate}")
#       if [ ! -e "${find3}"  ]; then
#               DN=$(( DN+3 )) 
#       fi
# done

get_data() {
        rundate="$2"
        echo "Downloading data for $rundate"
        DataLink="ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.${rundate}00"
        DataName="gfs.t00z.pgrb2.0p50.f0"$1
        wget "${DataLink}"/"${DataName}" -O ./"${rundate}"."${DataName}"
 }

export -f get_data

seq -f "%02g $(echo "${rundate//-}")" 0 3 75 | xargs -n 1 -P 10 -I {} bash -c 'get_data $@' _ {}

rm runlock.txt

end=$(date +%s)
secs=$((end-tot_start))
print_elapsed_time "Data-download" $secs

exit
