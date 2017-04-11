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

rundate1=$(date '+%Y-%m-%d' --date="1 days ago")
rundate2=$(date '+%Y-%m-%d' --date="0 days ago")
rundate3=$(date '+%Y-%m-%d' --date="1 days")

h="wrfout_d03_"
t="_00:00:00"
file1=$wrf_output/$h$rundate1$t
echo "$file1"

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
	sed -n 20,43p "$stn_name""$rundate1".txt > $rf_output/"$stn_name""$rundate2"-created-"$rundate2".txt
	sed -n 44,67p "$stn_name""$rundate1".txt > $rf_output/"$stn_name""$rundate3"-created-"$rundate2".txt

	rm "$stn_name""$rundate1".txt
	rm "$stn_name".nc
	rm "$stn_name".txt "$stn_name"2.txt
done

rm precip.nc
rm first.nc
rm second.nc
rm difference.nc timedata.txt timedata2.txt

exit;
