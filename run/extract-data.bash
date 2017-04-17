#!/bin/bash

lib_path="/opt/lib"
wrf_home="/mnt/disks/wrf-mod"

geog_home="$wrf_home/DATA/geog/"
gfs_home="$wrf_home/DATA/GFS/"

src_home="$wrf_home/wrf-scripts/src"
ncl_home="$wrf_home/wrf-scripts/ncl"
log_home="$wrf_home/logs"
log_file="extract.data."$(date +"%Y-%m-%d_%H%M")".log"

wrf_output="$wrf_home/OUTPUT"
rf_output="$wrf_output/RF"

echo "Redirecting logs to $log_home/$log_file"
mkdir -p $log_home
exec > "$log_home/$log_file"

export NETCDF="$lib_path"/netcdf

rundate1=$(date '+%Y-%m-%d' --date="0 days ago")
rundate2=$(date '+%Y-%m-%d' --date="1 days")

h="wrfout_d03_"
t="_00:00:00"
file1=$wrf_output/$h$rundate1$t
echo "$file1"

if [ -s "$file1" ]
then 
    echo " $file1 exists and is not empty. Extracting data... "
 else
    echo " $file1  does not exist, or is empty " 
    exit
fi

check_output=$rf_output/Kitulgala-3day-forecast-created-"$rundate1".txt
if [ -s "$check_output" ]
then 
    echo " $check_output exists and is not empty. Data already extracted!"
    exit
 else
    echo " $check_output  does not exist, or is empty. Extracting data..." 
fi


cd $wrf_output || exit

mkdir -p $rf_output

ncap   -s   "PRCP=RAINC+RAINNC+SNOWNC+GRAUPELNC" "$file1"  precip.nc
ncks   -v Times   -A    "$file1"   precip.nc
ncks -h -d Time,0,71,1 precip.nc first.nc
ncks -h -d Time,1,72,1 precip.nc second.nc
ncdiff second.nc first.nc difference.nc

declare -a stations=("13 44 Colombo"
        "21 44 Hanwella"
        "27 54 Holombuwa"
        "23 51 Attanagalla"
        "25 46 Glencourse"
        "30 44 Daraniyagala"
        "40 41 Norwood"
        "33 47 Kitulgala")

for station in "${stations[@]}"
do
        echo "Exctracting $station"
        IFS=', ' read -r -a array <<< "$station"
        we="${array[0]}"
        sn="${array[1]}"
        stn_name="${array[2]}"

        ncks -d west_east,"$we" -d south_north,"$sn" difference.nc "$stn_name".nc
        ncdump -v PRCP "$stn_name".nc > "$stn_name".txt
        ncdump -v Times "$stn_name".nc > timedata.txt
        sed "/netcdf "$stn_name" {/,/ PRCP =/d" "$stn_name".txt > "$stn_name"2.txt
        sed "/netcdf "$stn_name" {/,/ Times =/d" timedata.txt > timedata2.txt
        paste timedata2.txt "$stn_name"2.txt > "$stn_name""$rundate1".txt
        sed -n 1,72p "$stn_name""$rundate1".txt > $rf_output/"$stn_name"-3day-forecast-created-"$rundate1".txt
        sed -n 5,28p "$stn_name""$rundate1".txt > $rf_output/"$stn_name""$rundate1"-created-"$rundate1".txt
        sed -n 29,52p "$stn_name""$rundate1".txt > $rf_output/"$stn_name""$rundate2"-created-"$rundate1".txt

        rm "$stn_name""$rundate1".txt
        rm "$stn_name".nc
        rm "$stn_name".txt "$stn_name"2.txt
done

rm precip.nc
rm first.nc
rm second.nc
rm difference.nc timedata.txt timedata2.txt

exit;