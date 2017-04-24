#!/usr/bin/python

import time
import datetime as dt  # Python standard library datetime  module
import os
import sys
import subprocess
import numpy as np


def download_gfs_data(get_data_cmd, start_date):
    start_time = time.time()
    process = subprocess.call('%s %s' % (get_data_cmd, start_date.strftime('%Y%m%d')), shell=True)
    elapsed_time = time.time() - start_time

    return process, elapsed_time


def run_wrf(run_wrf_cmd, start_date, end_date):
    start_time = time.time()
    process = subprocess.call(
        '%s %s %s' % (run_wrf_cmd, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')), shell=True)
    elapsed_time = time.time() - start_time

    return process, elapsed_time


def main():
    wrf_home = '/mnt/disks/wrf-mod'
    gfs_home = wrf_home + '/DATA/GFS'
    wrf_output = wrf_home + '/OUTPUT'
    run_home = wrf_home + '/wrf-scripts/run'

    start_date = (dt.datetime.strptime(sys.argv[1], '%Y-%m-%d') if (len(sys.argv) > 1) else dt.datetime.today())
    end_date = (dt.datetime.strptime(sys.argv[2], '%Y-%m-%d') if (len(sys.argv) > 2) else
                dt.datetime.today() + dt.timedelta(days=1))
    period = sys.argv[3] if (len(sys.argv) > 3) else 3

    print 'WRF will be run from %s to %s for a period of %d days each day' % (
        start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), period)

    dates = np.arange(start_date, end_date, dt.timedelta(days=1)).astype(dt.datetime)

    get_data_cmd = run_home + '/get-hist-data.bash'
    run_wrf_cmd = run_home + '/only-wrf.bash'
    for date in dates:
        date1 = date + dt.timedelta(days=period)
        print 'WRF scheduled from %s to %s' % (date.strftime('%Y-%m-%d'), date1.strftime('%Y-%m-%d'))

        print 'Downloading data from %s. Running bash file %s' % (date.strftime('%Y%m%d'), get_data_cmd)
        process1, elapsed_time = download_gfs_data(get_data_cmd, date)
        print 'Data download completed for %s. Elapsed time %f' % (date.strftime('%Y%m%d'), elapsed_time)

        print 'Running wrf from %s to %s' % (date.strftime('%Y%m%d'), date1.strftime('%Y%m%d'))
        process2, elapsed_time = run_wrf_cmd(run_wrf_cmd, da)
        print 'WRF run completed from %s to %s. Elapsed time %f' % (
            date.strftime('%Y%m%d'), date1.strftime('%Y%m%d'), elapsed_time)


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
