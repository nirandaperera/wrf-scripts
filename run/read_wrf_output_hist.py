#!/usr/bin/python

import datetime as dt  # Python standard library datetime  module
import os

import numpy as np
import sys
import csv
import shapefile
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
from shapely.geometry import Polygon, Point, MultiPolygon, shape
import pandas as pd


def extract_time_data(nc_fid):
    times_len = len(nc_fid.dimensions['Time'])
    times = nc_fid.variables['Times'][0:times_len]
    return times_len, times


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


def extract_metro_colombo(_nc_fid, _date, _times, _wrf_output):
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

    output_dir = _wrf_output + '/colombo/created-' + _date.strftime('%Y-%m-%d')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for tm in range(0, len(_times) - 1):
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


def extract_weather_stations(_nc_fid, _date, _times, _weather_stations, _wrf_output):
    with open(_weather_stations, 'rb') as csvfile:
        stations = csv.reader(csvfile, delimiter=' ')
        stations_dir = _wrf_output + '/RF'
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


def extract_kelani_lower_basin_rainfall(_nc_fid, _date, _times, _kelani_basin_file, _wrf_output):
    lats = _nc_fid.variables['XLAT'][0, :, 0]
    lons = _nc_fid.variables['XLONG'][0, 0, :]

    points = np.genfromtxt(_kelani_basin_file, delimiter=',')

    kel_min_lon = np.min(points, 0)[1]
    kel_min_lat = np.min(points, 0)[2]
    kel_max_lon = np.max(points, 0)[1]
    kel_max_lat = np.max(points, 0)[2]

    lon_min = np.argmax(lons >= kel_min_lon) - 1
    lat_min = np.argmax(lats >= kel_min_lat) - 1
    lon_max = np.argmax(lons >= kel_max_lon)
    lat_max = np.argmax(lats >= kel_max_lat)

    prcp = _nc_fid.variables['RAINC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           _nc_fid.variables['RAINNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           _nc_fid.variables['SNOWNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           _nc_fid.variables['GRAUPELNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1]

    diff = prcp[1:len(_times), :, :] - prcp[0: len(_times) - 1, :, :]

    kel_lats = _nc_fid.variables['XLAT'][0, lat_min:lat_max + 1, 0]
    kel_lons = _nc_fid.variables['XLONG'][0, 0, lon_min:lon_max + 1]

    def get_bins(arr):
        sz = len(arr)
        return (arr[1:sz - 1] + arr[0:sz - 2]) / 2

    lat_bins = get_bins(kel_lats)
    lon_bins = get_bins(kel_lons)

    output_dir = _wrf_output + '/kelani-basin/created-' + _date.strftime('%Y-%m-%d')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = output_dir + '/RAINCELL.DAT'
    output_file = open(output_file_path, 'w')

    res = 60
    data_hours = len(_times) - 1
    start_ts = _date.strftime('%Y-%m-%d %H:%M:%S')
    end_ts = (_date + dt.timedelta(hours=data_hours - 1)).strftime('%Y-%m-%d %H:%M:%S')
    output_file.write("%d %d %s %s\n" % (res, data_hours, start_ts, end_ts))

    for h in range(0, data_hours):
        for point in points:
            rf_x = np.digitize(point[1], lon_bins)
            rf_y = np.digitize(point[2], lat_bins)
            output_file.write('%d %f\n' % (point[0], diff[h, rf_y, rf_x]))

    output_file.close()

    return lon_min, lat_min, lon_max, lat_max


def extract_kelani_upper_basin_mean_rainfall(nc_fid, date, times, kelani_basin_shp_file, wrf_output):
    def find_polygon(polygons, lat, lon):
        point = Point(lon, lat)
        for i, poly in enumerate(polygons.shapeRecords()):
            polygon = shape(poly.shape.__geo_interface__)
            if point.within(polygon):
                # print lat, lon, i
                return 1
        # print lat, lon, -1
        return 0

    kel_lon_min = 79.994117
    kel_lat_min = 6.754167
    kel_lon_max = 80.773182
    kel_lat_max = 7.229167

    lats = nc_fid.variables['XLAT'][0, :, 0]
    lons = nc_fid.variables['XLONG'][0, 0, :]

    lon_min = np.argmax(lons >= kel_lon_min) - 1
    lat_min = np.argmax(lats >= kel_lat_min) - 1
    lon_max = np.argmax(lons >= kel_lon_max)
    lat_max = np.argmax(lats >= kel_lat_max)

    polys = shapefile.Reader(kelani_basin_shp_file)

    kel_lats = nc_fid.variables['XLAT'][0, lat_min:lat_max + 1, lon_min:lon_max + 1]
    kel_lons = nc_fid.variables['XLONG'][0, lat_min:lat_max + 1, lon_min:lon_max + 1]

    prcp = nc_fid.variables['RAINC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           nc_fid.variables['RAINNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           nc_fid.variables['SNOWNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           nc_fid.variables['GRAUPELNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1]

    diff = prcp[1:len(times), :, :] - prcp[0: len(times) - 1, :, :]

    output_dir = wrf_output + '/kelani-upper-basin/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = output_dir + '/mean-rf-' + date.strftime('%Y-%m-%d') + '.txt'
    output_file = open(output_file_path, 'w')

    for t in range(0, len(times) - 1):
        cnt = 0
        sum = 0.0
        for y in range(0, len(kel_lats[:, 0])):
            for x in range(0, len(kel_lons[0, :])):
                if find_polygon(polys, kel_lats[y, x], kel_lons[y, x]):
                    cnt = cnt + 1
                    sum = sum + diff[t, y, x]
        output_file.write('%s %f\n' % (''.join(times[t, :]), sum / cnt))

    output_file.close()


def extract_kelani_upper_basin_mean_rainfall_sat(nc_fid, date, times, kelani_basin_shp_file, wrf_output):
    def find_polygon(polygons, lat, lon):
        point = Point(lon, lat)
        for i, poly in enumerate(polygons.shapeRecords()):
            polygon = shape(poly.shape.__geo_interface__)
            if point.within(polygon):
                # print lat, lon, i
                return 1
        # print lat, lon, -1
        return 0

    kel_lon_min = 79.994117
    kel_lat_min = 6.754167
    kel_lon_max = 80.773182
    kel_lat_max = 7.229167

    lats = nc_fid.variables['XLAT'][0, :, 0]
    lons = nc_fid.variables['XLONG'][0, 0, :]

    lon_min = np.argmax(lons >= kel_lon_min) - 1
    lat_min = np.argmax(lats >= kel_lat_min) - 1
    lon_max = np.argmax(lons >= kel_lon_max)
    lat_max = np.argmax(lats >= kel_lat_max)

    polys = shapefile.Reader(kelani_basin_shp_file)

    kel_lats = nc_fid.variables['XLAT'][0, lat_min:lat_max + 1, lon_min:lon_max + 1]
    kel_lons = nc_fid.variables['XLONG'][0, lat_min:lat_max + 1, lon_min:lon_max + 1]

    prcp = nc_fid.variables['RAINC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           nc_fid.variables['RAINNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           nc_fid.variables['SNOWNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1] + \
           nc_fid.variables['GRAUPELNC'][:, lat_min:lat_max + 1, lon_min:lon_max + 1]

    diff = prcp[1:len(times), :, :] - prcp[0: len(times) - 1, :, :]

    output_dir = wrf_output + '/kelani-upper-basin/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path = output_dir + '/mean-rf-' + date.strftime('%Y-%m-%d') + '.txt'
    output_file = open(output_file_path, 'w')

    for t in range(0, len(times) - 1):
        cnt = 0
        sum = 0.0
        for y in range(0, len(kel_lats[:, 0])):
            for x in range(0, len(kel_lons[0, :])):
                if find_polygon(polys, kel_lats[y, x], kel_lons[y, x]):
                    cnt = cnt + 1
                    sum = sum + diff[t, y, x]
        output_file.write('%s %f\n' % (''.join(times[t, :]), sum / cnt))

    output_file.close()


def add_buffer_to_kelani_upper_basin_mean_rainfall(date, wrf_output):
    cells = 9433

    content = []
    first_line = ''
    for i in range(3, -1, -1):
        file_name = wrf_output + '/kelani-basin/created-' + (date - dt.timedelta(days=i)).strftime(
            '%Y-%m-%d') + '/RAINCELL.DAT'

        if os.path.exists(file_name):
            with open(file_name) as myfile:
                first_line = next(myfile)
                if i != 0:
                    head = [next(myfile) for x in xrange(cells * 24)]
                else:
                    head = [line for line in myfile]
            content.extend(head)
        else:
            head = ['%d 0.0\n' % (x % cells + 1) for x in xrange(cells * 24 + 1)]
            content.extend(head)

    out_dir = wrf_output + '/kelani-basin/new-created-' + date.strftime('%Y-%m-%d')
    out_name = out_dir + '/RAINCELL.DAT'

    first_line = first_line.split()
    first_line[1] = str(int(first_line[1]) + 24 * 3)
    first_line[2] = (date - dt.timedelta(days=3)).strftime('%Y-%m-%d')

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_file = open(out_name, 'w')
    out_file.write(' '.join(first_line) + '\n')
    for line in content:
        out_file.write(line)
    out_file.close()


def concat_rainfall_files(date, wrf_output, weather_stations):
    with open(weather_stations, 'rb') as stations_file:
        rf_dir = wrf_output + '/RF'
        for station_name in stations_file:
            station_name = station_name.split()[0]
            if not os.path.exists(rf_dir):
                os.makedirs(rf_dir)

            out_file_path = rf_dir + '/' + station_name + '.csv'
            if not os.path.exists(out_file_path):
                with open(out_file_path, 'w') as out_file:
                    out_file.write("Timestamp, Value, Time, ValID\n")

            with open(out_file_path, 'a') as out_file:
                rf_file = rf_dir + '/' + station_name + '-' + date.strftime('%Y-%m-%d') + '.txt'
                with open(rf_file) as rf_file:
                    # next(rf_file)
                    i = 0
                    for line in rf_file:
                        ts = line.split()[0]
                        val = line.split()[1]
                        ref = int(dt.datetime.strptime('2017-04-01', '%Y-%m-%d').strftime('%s')) / 3600
                        epoch = int(dt.datetime.strptime(ts, '%Y-%m-%d_%H:%M:%S').strftime('%s')) / 3600 - ref
                        # epoch = dt.datetime.strptime(ts, '%Y-%m-%d_%H:%M:%S').strftime('%s')
                        val_id = station_name[0:5] + date.strftime('%y%m%d-') + str(i / 24)
                        out_file.write('%s, %s, %s, %s\n' % (ts, val, epoch, val_id))
                        i += 1


def concat_rainfall_files_1(date, wrf_output, weather_stations):
    with open(weather_stations, 'rb') as stations_file:
        rf_dir = wrf_output + '/RF'
        for station_name in stations_file:
            station_name = station_name.split()[0]
            if not os.path.exists(rf_dir):
                os.makedirs(rf_dir)

            df = None
            out_file_path = rf_dir + '/' + station_name + '-merged.csv'
            if os.path.exists(out_file_path):
                df = pd.read_csv(out_file_path)

            rf_file = rf_dir + '/' + station_name + '-' + date.strftime('%Y-%m-%d') + '.txt'
            rf_df = pd.read_csv(rf_file, header=None, delim_whitespace=True)
            rf_df.columns = ['time', 'f' + date.strftime('%y%m%d')]
            rf_df['time'] = rf_df['time'].apply(lambda x: int(dt.datetime.strptime(x, '%Y-%m-%d_%H:%M:%S').strftime('%s')))

            if df is not None:
                df_out = pd.merge(df, rf_df, on='time', how='outer')
                df_out.to_csv(out_file_path, index=False)
            else:
                rf_df.to_csv(out_file_path, index=False)


def main():
    start_date = (dt.datetime.strptime(sys.argv[1], '%Y-%m-%d') if (len(sys.argv) > 1)
                  else dt.datetime.today())
    end_date = (
        dt.datetime.strptime(sys.argv[2], '%Y-%m-%d') if (len(sys.argv) > 2) else start_date + dt.timedelta(
            days=1))
    wrf_home = sys.argv[3] if (len(sys.argv) > 3) else '/mnt/disks/wrf-mod'
    wrf_output = wrf_home + '/OUTPUT'
    weather_stations = wrf_home + '/wrf-scripts/src/stations.txt'

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
        extract_metro_colombo(nc_fid, date, times, wrf_output)

        print "##########################"
        print "Extract weather station rainfall"
        extract_weather_stations(nc_fid, date, times, weather_stations, wrf_output)

        print "##########################"
        print "Extract Kelani Basin point rainfall"
        kelani_basin_file = wrf_home + '/wrf-scripts/src/kelani-basin-points.txt'
        extract_kelani_lower_basin_rainfall(nc_fid, date, times, kelani_basin_file, wrf_output)

        print "##########################"
        print "Extract Kelani upper Basin mean rainfall"
        kelani_basin_shp_file = wrf_home + '/wrf-scripts/src/kelani-upper-basin.shp'
        extract_kelani_upper_basin_mean_rainfall(nc_fid, date, times, kelani_basin_shp_file, wrf_output)

        print "##########################"
        print "adding buffer to the RAINCELL.DAT file"
        add_buffer_to_kelani_upper_basin_mean_rainfall(date, wrf_output)

        print "##########################"
        print "Concat the RF of the weather stations 1"
        concat_rainfall_files(date, wrf_output, weather_stations)

        print "##########################"
        print "Concat the RF of the weather stations 2"
        concat_rainfall_files(date, wrf_output, weather_stations)

        nc_fid.close()


if __name__ == "__main__":
    main()
