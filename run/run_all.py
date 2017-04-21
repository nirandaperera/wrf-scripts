#!/usr/bin/python

import time
import datetime as dt  # Python standard library datetime  module
import os
import sys
import subprocess


def main():
    wrf_home = '/mnt/disks/wrf-mod'
    gfs_home = wrf_home + '/DATA/GFS'
    wrf_output = wrf_home + '/OUTPUT'
    run_home = wrf_home + '/wrf-scripts/run'

    start_date = (dt.datetime.strptime(sys.argv[1], '%Y-%m-%d') if (len(sys.argv) > 1) else dt.datetime.today())
    end_date = (dt.datetime.strptime(sys.argv[2], '%Y-%m-%d') if (len(sys.argv) > 2) else
                dt.datetime.today() + dt.timedelta(days=1))
    print 'Downloading data for %s' % start_date

    get_data_cmd = '.' + run_home + '/get-hist-data.bash'
    print 'Running bash file %s' % get_data_cmd
    Process = subprocess.call('%s %s' % (get_data_cmd, start_date), shell=True)


if __name__ == "__main__":
    main()



    # last_file_name = gfs_home + '/' + start_date.strftime('%Y%m%d') + '.gfs.t00z.pgrb2.0p50.f075'
    #
    # i = 5
    # while i > 0 and (not os.path.exists(last_file_name) or os.stat(last_file_name).st_size == 0):
    #     print "File %s does not exist. Downloading data" % last_file_name
    #     result = subprocess.call(run_home + '/get-daily-data.bash')
    #     i = i - 1
    #     if os.stat(last_file_name).st_size != 0:
    #         print "data downloaded!"
    #         break
    #     time.sleep(5 * 60)
    #
    # wrf_output_file = wrf_output + '/wrfout_d03_' + start_date.strftime('%Y-%m-%d') + '_00:00:00'
    #
    # i = 5
    # while i > 0 and (not os.path.exists(wrf_output_file) or os.stat(wrf_output_file).st_size == 0):
    #     print "wrf output %s does not exist. Running WRF" % last_file_name
    #     result = subprocess.call(run_home + '/run-wrf.bash')
    #     i = i - 1
    #     if os.stat(wrf_output_file).st_size != 0:
    #         print "WRF run complete!"
    #         break
    #     time.sleep(5 * 60)
