#!/usr/bin/python

import datetime as dt  # Python standard library datetime  module
import os

import numpy as np
import sys
import csv

from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/

# GLOBALS
wrf_home = '/home/nira/Desktop/temp'
wrf_output = '/home/nira/Desktop/temp'
weather_stations = '/home/nira/IdeaProjects/WrfRainfall/stations.txt'
start_date = dt.datetime.strptime('2017-03-27', '%Y-%m-%d')
end_date = dt.datetime.strptime('2017-03-28', '%Y-%m-%d')


def extract_time_data(_nc_fid):
    _times_len = len(_nc_fid.dimensions['Time'])
    _times = _nc_fid.variables['Times'][0:_times_len]
    return _times_len, _times


def ncdump(_nc_fid, verb=True):
    def print_ncattr(key):
        try:
            print "\t\ttype:", repr(_nc_fid.variables[key].dtype)
            for ncattr in _nc_fid.variables[key].ncattrs():
                print '\t\t%s:' % ncattr, \
                    repr(_nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            print "\t\tWARNING: %s does not contain variable attributes" % key

    # NetCDF global attributes
    _nc_attrs = _nc_fid.ncattrs()
    if verb:
        print "NetCDF Global Attributes:"
        for nc_attr in _nc_attrs:
            print '\t%s:' % nc_attr, repr(_nc_fid.getncattr(nc_attr))
    _nc_dims = [dim for dim in _nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print "NetCDF dimension information:"
        for dim in _nc_dims:
            print "\tName:", dim
            print "\t\tsize:", len(_nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    _nc_vars = [var for var in _nc_fid.variables]  # list of nc variables
    if verb:
        print "NetCDF variable information:"
        for var in _nc_vars:
            if var not in _nc_dims:
                print '\tName:', var
                print "\t\tdimensions:", _nc_fid.variables[var].dimensions
                print "\t\tsize:", _nc_fid.variables[var].size
                print_ncattr(var)
    return _nc_attrs, _nc_dims, _nc_vars


def extract_metro_colombo(_nc_fid, _date, _times):
    lat_min = 41
    lat_max = 47
    lon_min = 11
    lon_max = 17
    cell_size = 0.02723
    no_data_val = -99

    lats = _nc_fid.variables['XLAT'][0, lat_min:lat_max + 1, 0]  # extract/copy the data
    lons = _nc_fid.variables['XLONG'][0, 0, lon_min:lon_max + 1]

    prcp = _nc_fid.variables['RAINC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           _nc_fid.variables['RAINNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           _nc_fid.variables['SNOWNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           _nc_fid.variables['GRAUPELNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1]

    diff = prcp[1:73, :, :] - prcp[0:72, :, :]

    width = len(lons)
    height = len(lats)

    output_dir = wrf_output + '/colombo/created-' + _date.strftime('%Y-%m-%d')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for tm in range(0, 10): # len(_times) - 1):
        output_file_path = output_dir + '/rain-' + ''.join(_times[tm, :]) + '.txt'

        output_file = open(output_file_path, 'w')

        output_file.write('NCOLS %d\n' % width)
        output_file.write('NROWS %d\n' % height)
        output_file.write('XLLCORNER %f\n' % lons[0])
        output_file.write('YLLCORNER %f\n' % lats[0])
        output_file.write('CELLSIZE %f\n' % cell_size)
        output_file.write('NODATA_VALUE %d\n' % no_data_val)

        for y in range(0, height):
            for x in range(0, width):
                output_file.write('%f ' % diff[tm, y, x])
            output_file.write('\n')

        output_file.close()


def extract_weather_stations(_nc_fid, _date, _times, _weather_stations):
    with open(_weather_stations, 'rb') as csvfile:
        stations = csv.reader(csvfile, delimiter=' ')
        stations_dir = wrf_output + '/RF'
        if not os.path.exists(stations_dir):
            os.makedirs(stations_dir)
        for row in stations:
            print ' '.join(row)
            lon = row[1]
            lat = row[2]

            station_prcp = _nc_fid.variables['RAINC'][:, lat, lon] + \
                           _nc_fid.variables['RAINNC'][:, lat, lon] + \
                           _nc_fid.variables['SNOWNC'][:, lat, lon] + \
                           _nc_fid.variables['GRAUPELNC'][:, lat, lon]

            station_diff = station_prcp[1:len(_times)] - station_prcp[0:len(_times) - 1]

            station_file_path = stations_dir + '/' + row[0] + '-' + _date.strftime('%Y-%m-%d') + '.txt'
            station_file = open(station_file_path, 'w')

            for t in range(0, len(_times) - 1):
                station_file.write('%s %f\n' % (''.join(_times[t, :]), station_diff[t]))
            station_file.close()


def main():
    global wrf_home
    global wrf_output
    global weather_stations
    global start_date
    global end_date

    wrf_home = '/mnt/disks/wrf-mod'
    wrf_output = wrf_home + '/OUTPUT'
    weather_stations = wrf_home + '/wrf-scripts/src/stations.txt'
    start_date = (dt.datetime.strptime(sys.argv[1], '%Y-%m-%d') if (len(sys.argv) > 1) else dt.datetime.today())
    end_date = (
        dt.datetime.strptime(sys.argv[2], '%Y-%m-%d') if (len(sys.argv) > 2) else dt.datetime.today() + dt.timedelta(
            days=1))

    print "##########################"
    print "WRF dir = %s" % wrf_home
    print "WRF output dir = %s" % wrf_output
    print "Weather stations file output dir = %s" % weather_stations
    print "Start date = %s" % start_date.strftime('%Y-%m-%d')
    print "End date = %s" % end_date.strftime('%Y-%m-%d')

    dates = np.arange(start_date, end_date, dt.timedelta(days=1)).astype(dt.datetime)

    for date in dates:
        print "##########################"
        nc_f = wrf_output + '/wrfout_d03_' + date.strftime('%Y-%m-%d') + '_00:00:00'
        print "File = %s" % nc_f

        if os.stat(nc_f).st_size == 0:
            print "File %s does not exist. Exit!"
            sys.exit(0)

        nc_fid = Dataset(nc_f, 'r')

        # and create an instance of the ncCDF4 class
        # nc_attrs, nc_dims, nc_vars = ncdump(nc_fid, False)

        print "##########################"
        print "Extract time data"
        times_len, times = extract_time_data(nc_fid)

        print "##########################"
        print "Extract rainfall data for the metro colombo area"
        extract_metro_colombo(nc_fid, date, times)

        print "##########################"
        print "Extract weather station rainfall"
        extract_weather_stations(nc_fid, date, times, weather_stations)

        nc_fid.close()


if __name__ == "__main__":
    main()
