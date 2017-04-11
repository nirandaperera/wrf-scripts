#!/bin/bash

wrf_home="/mnt/disks/wrf-mod"

log_home="$wrf_home/logs"
log_file="move.data."$(date +"%Y-%m-%d_%H%M")".log"

wrf_output="$wrf_home/OUTPUT"

echo "Redirecting logs to $log_home/$log_file"
mkdir -p $log_home
exec > "$log_home/$log_file"


day1=$(date '+%Y-%m-%d' --date "-7 days")
# day2=$(date '+%Y-%m-%d' --date "-3 days")

File1="wrfout_d01_$day1*"
File2="wrfout_d02_$day1*"
File3="wrfout_d03_$day1*"
echo $File1
echo $File2
echo $File3

cd $wrf_output  || exit

rm -rf $File1 
rm -rf $File2 

# mv $File3 /run/media/sherath/_wrfout/SriLanka/d03/

# cd RFdata
# mv CF$day1.txt /run/media/sherath/_wrfout/SriLanka/RFdata/
# rm /var/www/html/slf/SLD03$day2.gif
# rm /var/www/html/slf/SLD02$day2.gif
exit;
