import numpy as np
from matplotlib import pyplot as plt
import matplotlib as m
from matplotlib import ticker, cm
from math import *
import matplotlib.colors as mcolors
from mpl_toolkits.basemap import  Basemap
import pickle
from matplotlib.patches import Polygon

def plot_stations(stations):
    min_longitude = None
    max_longitude = None
    min_latitude = None
    max_latitude = None
    longitudes = []
    latitudes = []
    for station_name,value in stations.items():
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
    print('min_longitude=%s'%min_longitude)
    print('max_longitude=%s' % max_longitude)
    print('min_latitude =%s' % min_latitude )
    print('max_latitude =%s' % max_latitude )
    
    
    # map = Basemap(llcrnrlon = min_longitude, llcrnrlat = min_latitude, urcrnrlon = max_longitude, urcrnrlat = max_latitude ,resolution = 'f')
    map = Basemap(llcrnrlon=min_longitude, llcrnrlat=min_latitude, urcrnrlon=max_longitude, urcrnrlat=max_latitude)
    # map.fillcontinents(color='coral', lake_color='aqua')
    x, y = map(longitudes, latitudes)
    map.scatter(x, y, marker='o', color='m')
    map.drawparallels(np.arange(min_latitude, max_latitude, 1), labels=[1, 0, 0, 0])
    map.drawmeridians(np.arange(min_longitude, max_longitude, 1), labels=[0, 0, 0, 1])
    
    return map

if __name__ == '__main__':
    # map = Basemap(projection = 'ortho', lat_0 = 0, lon_0 = 0)
    # map = Basemap(llcrnrlon=80.33,
    #         llcrnrlat=3.01,
    #         urcrnrlon=138.16,
    #         urcrnrlat=56.123,
    #         resolution='h', projection='cass', lat_0=42.5, lon_0=120)
    # map.drawcoastlines()
    # map.shadedrelief()
    # map.etopo(scale=0.5, alpha=0.5)
    # plt.show()
    
    
    # with open('station_data.pickle', 'rb') as f:
    #     data = pickle.load(f)
    # map = plot_stations(data['stations'])
    # fig = plt.figure()
    # ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    # map.ax = ax1
    # shp_info = map.readshapefile('CHN_adm_shp/CHN_adm3', 'states', drawbounds=False)
    #
    # for info, shp in zip(map.states_info, map.states):
    #     proid = info['NAME_1']
    #     if proid == 'Sichuan':
    #         poly = Polygon(shp, facecolor='w', edgecolor='b', lw=0.2)
    #         ax1.add_patch(poly)
    #
    # map.drawcountries()
    # # map.scatter(x, y, marker='o', color='m')
    # # map.drawcoastlines()
    # plt.show()



    fig = plt.figure()
    ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    bmap = Basemap(llcrnrlon=115, llcrnrlat=23, urcrnrlon=121, urcrnrlat=29,
                   projection='lcc', lat_1=33, lat_2=45, lon_0=120, ax=ax1)
    # bmap = Basemap(llcrnrlon=102, llcrnrlat=29, urcrnrlon=106, urcrnrlat=32,
    #                ax=ax1)

    shp_info = bmap.readshapefile('CHN_adm_shp/CHN_adm3', 'states', drawbounds=False)

    for info, shp in zip(bmap.states_info, bmap.states):
        proid = info['NAME_1']
        if proid == 'Sichuan':
            poly = Polygon(shp, facecolor='w', edgecolor='b', lw=0.2)
            ax1.add_patch(poly)

    bmap.drawcoastlines()
    bmap.drawcountries()
    bmap.drawparallels(np.arange(23, 29, 2), labels=[1, 0, 0, 0])
    bmap.drawmeridians(np.arange(115, 121, 2), labels=[0, 0, 0, 1])
    plt.show()