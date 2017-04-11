#!/bin/bash

tot_start=$(date +%s)

lib_path="/opt/lib"
wrf_home="/mnt/disks/wrf-mod"

geog_home="$wrf_home/DATA/geog/"
gfs_home="$wrf_home/DATA/GFS/"

src_home="$wrf_home/wrf-scripts/src"
run_home="$wrf_home/wrf-scripts/run"
ncl_home="$wrf_home/wrf-scripts/ncl"
log_home="$wrf_home/logs"
log_file="only.wrf.run.log"

wrf_output="$wrf_home/OUTPUT"

echo "Redirecting logs to $log_home/$log_file"
mkdir -p $log_home
exec > "$log_home/$log_file"

export NETCDF="$lib_path"/netcdf
export LD_LIBRARY_PATH="$lib_path"/mpich/lib:"$lib_path"/grib2/lib:$LD_LIBRARY_PATH
export LD_INCLUDE_PATH="$lib_path"/mpich/include:/usr/include:"$lib_path"/grib2/include:$LD_INCLUDE_PATH
export PATH=$PATH:"$lib_path"/mpich/bin/

echo "WRF run start"

rundate=$(date '+%Y%m%d' --date="1 days ago")
year1=${rundate:0:4}
month1=${rundate:4:2}
date1=${rundate:6:2}

rundate2=$(date '+%Y%m%d' --date " 2 days")
year2=${rundate2:0:4}
month2=${rundate2:4:2}
date2=${rundate2:6:2}


cd $wrf_home/WRFV3/test/em_real/ || exit


start=$(date +%s)
mpirun -np 4 ./wrf.exe
end=$(date +%s)
secs=$((end-start))
printf 'wrf.exe Time elapsed %dh:%dm:%ds\n' $(($secs/3600)) $(($secs%3600/60)) $(($secs%60))

echo "WRF run completed"


echo "Move WRF Output"
mkdir -p $wrf_output
mv wrfout_d0* $wrf_output/ 
echo "Move WRF Output completed"


echo "Running NCL scripts"
cd $run_home || exit
./create-images.bash

echo "Extracting data"
cd $run_home || exit
./extract-data.bash

# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_predicted_observed_dailyinputs.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Daraniyagala.py 
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_GlencourseF.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Hanwella.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Holombuwa.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Kitulgala.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Norwood.py
# cp *.pdf /var/www/html/slg/
# mv *.pdf /run/media/sherath/_wrfout/SriLanka/Graphs/

rm -f wrflock.txt

end=$(date +%s)
secs=$((end-tot_start))
printf 'completed! Time elapsed %dh:%dm:%ds\n' $(($secs/3600)) $(($secs%3600/60)) $(($secs%60))

exit;
