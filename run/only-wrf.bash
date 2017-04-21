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

if [ -z "$1" ]; then
    start_date=$(date '+%Y%m%d' --date="0 days ago")
    else
    start_date=$1
fi

log_file="wrf.run.$start_date-$(date +"%Y-%m-%d_%H%M").log"

wrf_output="$wrf_home/OUTPUT"

echo "Redirecting logs to $log_home/$log_file"
mkdir -p $log_home
exec > "$log_home/$log_file"

export NETCDF="$lib_path"/netcdf
export LD_LIBRARY_PATH="$lib_path"/mpich/lib:"$lib_path"/grib2/lib:$LD_LIBRARY_PATH
export LD_INCLUDE_PATH="$lib_path"/mpich/include:/usr/include:"$lib_path"/grib2/include:$LD_INCLUDE_PATH
export PATH=$PATH:"$lib_path"/mpich/bin/


year1=${start_date:0:4}
month1=${start_date:4:2}
date1=${start_date:6:2}

if [ -z "$2" ]; then
    end_date=$(date '+%Y%m%d' --date "3 days")
    else
    end_date=$2
fi
year2=${end_date:0:4}
month2=${end_date:4:2}
date2=${end_date:6:2}

echo "WRF run start $start_date to $end_date"

cd $gfs_home || exit

find1="${start_date}.gfs.t00z.pgrb2.0p50.f075"
if [ -f "${find1}" ]; then
        find2=$(find ./ -size 0 | grep "${start_date}")
        if [ ! -e "${find2}" ];
                then
                echo "${start_date} Data available";
        else
                echo "Data not yet available";
                exit;
        fi
else
        echo "Data not yet available";
        exit;
fi

function print_elapsed_time {
	printf '%s - Time elapsed %dh:%dm:%ds\n' "$1" $(($2/3600)) $(($2%3600/60)) $(($2%60))
}

cd $wrf_home || exit

lockfile="wrflock.txt"
if [ -f ${lockfile} ]
        then
        echo "Simulation has already started";
        exit;
else
        echo "start simulation ${start_date}";
        touch wrflock.txt
fi

ulimit -s unlimited
mpdboot

cd $wrf_home/WPS || exit

sed -e 's@YY1@'$year1'@g;s@MM1@'$month1'@g;s@DD1@'$date1'@g;s@YY2@'$year2'@g;s@MM2@'$month2'@g;s@DD2@'$date2'@g;s@GEOG@'$geog_home'@g' $src_home/namelist.wps2 > namelist.wps
rm -f FILE:*
rm -f PFILE:*
rm -f met_em*

ln -sf ungrib/Variable_Tables/Vtable.NAM Vtable

./link_grib.csh $gfs_home/"$start_date"

start=$(date +%s)
./ungrib.exe
end=$(date +%s)
secs=$((end-start))
print_elapsed_time "Ungrib" $secs

start=$(date +%s)
./geogrid.exe
end=$(date +%s)
secs=$((end-start))
print_elapsed_time "Geogrid" $secs

start=$(date +%s)
./metgrid.exe
end=$(date +%s)
secs=$((end-start))
print_elapsed_time "Metgrid" $secs

cd $wrf_home/WRFV3/test/em_real/ || exit

sed -e 's@YY1@'$year1'@g;s@MM1@'$month1'@g;s@DD1@'$date1'@g;s@YY2@'$year2'@g;s@MM2@'$month2'@g;s@DD2@'$date2'@g' $src_home/namelist.input2 > namelist.input
rm -f met_em*
rm -f rsl*

ln -sf $wrf_home/WPS/met_em.d0* .

start=$(date +%s)
mpirun -np 4 ./real.exe
end=$(date +%s)
secs=$((end-start))
print_elapsed_time "Real.exe" $secs


start=$(date +%s)
mpirun -np 4 ./wrf.exe
end=$(date +%s)
secs=$((end-start))
print_elapsed_time "wrf.exe" $secs

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
#./extract-data.bash
python read_wrf_output.py

# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_predicted_observed_dailyinputs.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Daraniyagala.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_GlencourseF.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Hanwella.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Holombuwa.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Kitulgala.py
# /opt/Python/anaconda3/bin/python3.5 Plot_Rainfall_Norwood.py
# cp *.pdf /var/www/html/slg/
# mv *.pdf /run/media/sherath/_wrfout/SriLanka/Graphs/

rm -f $wrf_home/wrflock.txt

end=$(date +%s)
secs=$((end-tot_start))
print_elapsed_time "completed!" $secs

exit;
