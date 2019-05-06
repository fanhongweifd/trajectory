import pandas as pd
import numpy as np
import os
import sys
from collections import defaultdict
import time
import pickle
import chardet
from calculate import CalcData
from tools import *


def load_environment_data(dir_path):
    """
    该函数的作用是load国控站的数据
    :param dir_path: 是国控站数据的文件夹的地址
    :return stations_info: 存有每一时刻的每个站点的pm2.5    stations_info[time][station][pm25]
    :return stations: 存有每个站点的code和经纬度
    """
    stations = defaultdict(dict)
    stations_info = defaultdict(dict)
    
    csv_files = os.popen('find ' + dir_path + ' -name *.csv').readlines()
    for csv_path in csv_files:
        csv_path = csv_path.strip()
        print('csv_path=%s'%csv_path)
        csv_data = pd.read_csv(csv_path)
        station_code = csv_data.iloc[:, csv_data.columns == 'station_code'].values
        station_pm2_5 = csv_data.iloc[:, csv_data.columns == 'pm2_5'].values
        station_pubtime = csv_data.iloc[:, csv_data.columns == 'pubtime'].values
        station_longitude = csv_data.iloc[:, csv_data.columns == 'longitude'].values
        station_latitude = csv_data.iloc[:, csv_data.columns == 'latitude'].values
        
        for idx in range(len(station_code)):
            code = station_code[idx][0]
            pm2_5 = station_pm2_5[idx][0]
            pubtime = station_pubtime[idx][0]
            stamp_time = int(time.mktime(time.strptime(pubtime, "%Y-%m-%d %H:%M:%S")))
            longitude = float(station_longitude[idx][0])
            latitude = float(station_latitude[idx][0])
            if not code in stations:
                stations[code]['longitude'] = longitude
                stations[code]['latitude'] = latitude
            if not stamp_time in  stations:
                stations_info[stamp_time] = defaultdict(dict)
            stations_info[stamp_time][code]['pm25'] = pm2_5
    
    return stations_info, stations


def change_wind_angle(ori_angle):
    new_angle = 270 - ori_angle
    if new_angle<0:
        new_angle = new_angle + 360
    return new_angle
    
    
def load_wind_data(file_path, change_angle=True):
    """
    读取气象站的数据，包括气象站的经纬度和风向风速
    :param file_path: 数据路径
    :return citys: 县的经纬度
    :return citys_wind: 县的每一时刻的风力风向
    """
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    csv_data = pd.read_csv(file_path, encoding=result['encoding'])
    # csv_data = pd.read_csv(file_path)
    citys = defaultdict(dict)
    citys_wind = defaultdict(dict)
    city_name = csv_data.iloc[:, csv_data.columns == '县'].values
    city_longitude = csv_data.iloc[:, csv_data.columns == '经度'].values
    city_latitude = csv_data.iloc[:, csv_data.columns == '纬度'].values
    wind_direction = csv_data.iloc[:, csv_data.columns == '风向'].values
    wind_power = csv_data.iloc[:, csv_data.columns == '风力'].values
    pubtime = csv_data.iloc[:, csv_data.columns == '时间'].values
    for idx in range(len(city_name)):
        name = city_name[idx][0]
        if name not in citys:
            citys[name]['longitude'] = float(city_longitude[idx][0])
            citys[name]['latitude'] = float(city_latitude[idx][0])
        stamp_time = int(time.mktime(time.strptime(pubtime[idx][0], "%Y/%m/%d %H:%M")))
        if not stamp_time in citys_wind:
            citys_wind[stamp_time] = defaultdict(dict)
        if change_angle:
            citys_wind[stamp_time][name]['wind_power'] = change_wind_angle(wind_power[idx][0])
        else:
            citys_wind[stamp_time][name]['wind_power'] = wind_power[idx][0]
        citys_wind[stamp_time][name]['wind_direction'] = wind_direction[idx][0]
    return citys, citys_wind


def pair_city_stations(stations, citys):
    """
    按照最近的距离给国控站分配气象站
    :param  stations:国控站及坐标
    :param  citys:气象站及坐标
    :return: stations：增加了每个站点对应的气象站
    """
    calc = CalcData(citys)
    stations = calc.inter_distance(stations)
    return stations


def merge_data(stations, stations_info, citys, citys_wind):
    """
    合成国控站带有风向风速的数据
    :return: stations_info
    """
    stations = pair_city_stations(stations, citys)
    for date_time in stations_info:
        if date_time in citys_wind:
            wind_info = citys_wind[date_time]
            for station_name in stations_info[date_time]:
                min_distance_station = stations[station_name]['min_distance_station']
                if min_distance_station in wind_info:
                    stations_info[date_time][station_name]['wind_power'] = wind_info[min_distance_station]['wind_power']
                    stations_info[date_time][station_name]['wind_direction'] = wind_info[min_distance_station]['wind_direction']
        else:
            print('date time: %s not in wind information'% timestamp_to_string(date_time))
    return stations, stations_info
            
    


if __name__ == '__main__':
    stations_info, stations = load_environment_data('/data/tag/pytorch/trajectory/空气质量数据')
    save_data = {"stations_info":stations_info,
                 "stations":stations}
    with open('station_data.pickle', 'wb') as f:
        pickle.dump(save_data, f)
    citys, citys_wind = load_wind_data('/data/tag/pytorch/trajectory/气象数据.csv')
    save_data = {"citys":citys,
                 "citys_wind":citys_wind}
    with open('city_wind.pickle', 'wb') as f:
        pickle.dump(save_data, f)
    
    with open('city_wind.pickle','rb') as f:
        wind_data = pickle.load(f)
    with open('station_data.pickle','rb') as f:
        station_data = pickle.load(f)
    stations = station_data['stations']
    stations_info = station_data['stations_info']
    citys = wind_data['citys']
    citys_wind = wind_data['citys_wind']
    stations, stations_info = merge_data(stations, stations_info, citys, citys_wind)
    save_data = {"stations_info":stations_info,
                 "stations":stations}
    with open('train_data.pickle', 'wb') as f:
        pickle.dump(save_data, f)