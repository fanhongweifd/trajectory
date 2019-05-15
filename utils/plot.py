import numpy as np
from matplotlib import pyplot as plt
from math import *
from mpl_toolkits.basemap import Basemap
import pickle
from matplotlib.patches import Polygon
import argparse
import os


def plot_link(begin_station_name, next_station_name, stations):
    begin_x_y = [stations[begin_station_name]['longitude'], stations[begin_station_name]['latitude']]
    next_x_y = [stations[next_station_name]['longitude'], stations[next_station_name]['latitude']]
    # plt.plot([begin_x_y[0], next_x_y[0]], [begin_x_y[1], next_x_y[1]], 'r')
    plt.arrow(begin_x_y[0], begin_x_y[1], next_x_y[0]-begin_x_y[0], next_x_y[1]-begin_x_y[1], length_includes_head=True,head_width=0.1, head_length=0.1, fc='r', ec='b')


def plot_stations_link(begin_station_name, next_stations, stations):
    if next_stations:
        for next_station in next_stations.keys():
            next_station_name, _ = next_station
            plot_link(begin_station_name, next_station_name, stations)
            if next_stations[next_station]:
                plot_stations_link(next_station_name, next_stations[next_station], stations)



if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument('--trajectory_path', type=str, default='../results/trajectory_result.pickle', help='data path')
    parser.add_argument('--station_path', type=str, default='station_data.pickle', help='data path')
    parser.add_argument('--save_image_path', type=str, default='image', help='data path')
    
    args = parser.parse_args()
    with open(args.trajectory_path, 'rb') as f:
        result = pickle.load(f)
    
    with open(args.station_path, 'rb') as f:
        data = pickle.load(f)
        
    if not os.path.exists(args.save_image_path):
        os.mkdir(args.save_image_path)
        
    stations = data['stations']
    min_longitude = None
    max_longitude = None
    min_latitude = None
    max_latitude = None
    longitudes = []
    latitudes = []
    for station_name, value in stations.items():
        longitudes.append(value['longitude'])
        latitudes.append(value['latitude'])
        if not min_longitude:
            min_longitude = value['longitude']
            max_longitude = value['longitude']
            min_latitude = value['latitude']
            max_latitude = value['latitude']
        if value['longitude'] > max_longitude:
            max_longitude = value['longitude']
        if value['longitude'] < min_longitude:
            min_longitude = value['longitude']
        if value['latitude'] > max_latitude:
            max_latitude = value['latitude']
        if value['latitude'] < min_latitude:
            min_latitude = value['latitude']
    
    min_longitude = int(min_longitude)
    max_longitude = ceil(max_longitude)
    min_latitude = int(min_latitude)
    max_latitude = ceil(max_latitude)
    print('min_longitude=%s' % min_longitude)
    print('max_longitude=%s' % max_longitude)
    print('min_latitude =%s' % min_latitude)
    print('max_latitude =%s' % max_latitude)

    for data_time in result:
        bmap = Basemap(llcrnrlon=min_longitude, llcrnrlat=min_latitude, urcrnrlon=max_longitude, urcrnrlat=max_latitude)
        
        fig = plt.figure()
        ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        plt.plot(longitudes, latitudes, 'ok', markersize=5)
        
        for start_station in result[data_time]:
            plot_stations_link(start_station, result[data_time][start_station], stations)
        
        shp_info = bmap.readshapefile('CHN_adm_shp/CHN_adm3', 'states', drawbounds=False)
        for info, shp in zip(bmap.states_info, bmap.states):
            proid = info['NAME_1']
            if proid == 'Sichuan':
                poly = Polygon(shp, facecolor='w', edgecolor='b', lw=0.2)
                ax1.add_patch(poly)
        
        bmap.drawparallels(np.arange(min_latitude, max_latitude, 1), labels=[1, 0, 0, 0])
        bmap.drawmeridians(np.arange(min_longitude, max_longitude, 1), labels=[0, 0, 0, 1])
    
        plt.savefig('image/'+data_time+'.png')
