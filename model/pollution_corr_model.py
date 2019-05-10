import numpy as np
import os
import sys
import pickle
from collections import defaultdict
from utils.calculate import sub_angle, merge_vector, get_corr
from data.public_parameter import wind_power_set
from data.public_parameter import chengdu_stations
from utils.tools import timestamp_to_string
import numpy as np
import math

"""
_____________________________________General description__________________________________________

该方案的最终目的是：得到污染物向中心区域传播的路径
采用的核心方法：
1) 提取出每个站点污染物的上升趋势
2) 计算不同站点间上升趋势的相关性（用相关系数衡量）
3) 若两个站点间污染物上升趋势间的相关性很高，则判断是否两个站点间的上升符合风的传播路径。
4) 判断传播路径是否向中心区域的方向。
5）判断是否抵达中心区域
"""


def check_rise_trend(pollution_list, pollution_increase, pollution_thres):
    """
    判断污染是上升趋势
    :param pollution_list:
    :param pollution_increase:
    :param pollution_thres:
    :return:
    """
    if min(pollution_list) != pollution_list[0]:
        return False
    if max(pollution_list) - min(pollution_list) < pollution_increase:
        return False
    if max(pollution_list) < pollution_thres:
        return False
    return True


def get_rise_trend(stations_info, time_step=5, pollution_increase=50, pollution_thres=100):
    """
    得到污染物符合上升趋势的站点和对应的起始时刻
    判断上升趋势条件如下：
    在连续的时间段内（time_step）默认是5小时
    pm累计上升大于设定值（pollution_increase）
    并且污染物最高值大于设定的阈值（pollution_increase）
    并且第一个值是最小的
    :param stations_info:
    :return: stations_trend
    """
    assert time_step >= 1, 'time_step must more than 1, but now is %s' % time_step
    stations_trend = defaultdict(dict)
    date_time = list(stations_info.keys())
    date_time.sort()
    for idx, begin_time in enumerate(date_time[0:-4]):
        continue_step = True
        for step_i in range(1, time_step):
            # 这里由于数据都是间隔一个小时，所以可以这样判断是否是连续数据。
            if step_i * 3600 + begin_time != date_time[idx + step_i]:
                continue_step = False
        if continue_step:
            time_list = [date_time[idx + i] for i in range(time_step)]
            for station in stations_info[begin_time]:
                wind_power_list = []
                for time_single in time_list:
                    if station in stations_info[time_single]:
                        if 'wind_power' in stations_info[time_single][station]:
                            wind_power_list.append(stations_info[time_single][station]['wind_power'])
                pollution_list = []
                for time_single in time_list:
                    if station in stations_info[time_single]:
                        if 'pm25' in stations_info[time_single][station]:
                            pollution_list.append(stations_info[time_single][station]['pm25'])
                wind_direction_list = []
                for time_single in time_list:
                    if station in stations_info[time_single]:
                        if 'wind_direction' in stations_info[time_single][station]:
                            wind_direction_list.append(stations_info[time_single][station]['wind_direction'])
                
                if len(pollution_list) == len(wind_power_list) == len(wind_direction_list) == time_step:
                    if check_rise_trend(pollution_list, pollution_increase, pollution_thres):
                        stations_trend[begin_time][station] = dict(pollution=pollution_list, wind_power=wind_power_list,
                                                                   wind_direction=wind_direction_list)
    return stations_trend


def get_reasonable_trans(begin_station, end_station, max_angle=45):
    """
    判断从begin_station传输到end_station是否合理，判断准则如下：
    如果 end_station 不是成都市区内的国控站，那么：
    1. end_station要比begin_station距离成都市区更近
    2. end_station到成都市区的方向和begin_station到成都市区的方向要一致，或之间的夹角小于某个角度（这是确保路线上不会有大的波动）
    这样提前将每个国控站点有可能传播到的下一个站点计算出来
    :param begin_station: 起始站点
    :param end_station: 下一个站点
    :return:
    """
    if begin_station['center_distance'] < end_station['center_distance']:
        return False
    if sub_angle(begin_station['center_distance'], end_station['center_distance']) > max_angle:
        return False
    return True


def calc_wind_time(begin_station_wind, end_station, includedAngle=30, long_time=24):
    """
    判断begin_station的风能否吹到end_station，如果可以，在什么区间段内能够吹到，判断准则如下：
    1. begin_station的风向与begin_station到end_station的方向间的夹角应该小于某个角度（angle_thres）
    2. 根据风速的区间来计算到达end_station的最短时间和最长时间(这里设置了最长时间不能超过24小时，不然不可信)
    3. begin_station_wind可以是一个list，如果是这样，那么应该限定风向间的方差，这个后面加
    
    :param begin_station_wind:
    :param end_station:
    :return:
    """
    wind_direction = begin_station_wind['wind_direction']
    wind_min_speed = [wind_power_set[int(wind)]['min'] for wind in begin_station_wind['wind_power']]
    wind_max_speed = [wind_power_set[int(wind)]['max'] for wind in begin_station_wind['wind_power']]
    merge_min_speed, merge_angle = merge_vector(wind_min_speed, wind_direction)
    merge_max_speed, merge_angle = merge_vector(wind_max_speed, wind_direction)
    print('begin_station:%s'%begin_station_wind['name'])
    print("end_station:%s"%end_station)
    angle = begin_station_wind['angle'][end_station]
    distance = begin_station_wind['distance'][end_station]
    include_angle = sub_angle(merge_angle, angle)
    if include_angle > includedAngle:
        return False
    # 计算到达的时间区间
    max_arrive_time = distance / (math.cos(include_angle * math.pi / 180) * merge_min_speed)
    min_arrive_time = distance / (math.cos(include_angle * math.pi / 180) * merge_max_speed)
    max_arrive_time = math.ceil(max_arrive_time)
    min_arrive_time = int(min_arrive_time)
    if min_arrive_time > long_time:
        False
    if max_arrive_time > long_time:
        max_arrive_time = long_time
    return min_arrive_time, max_arrive_time


def check_station_corr(begin_station_value, end_station_value, corr_thres=0.8):
    """
    判断两站点间的相关系数，若相关系数大于设定值，则判定二者相关
    :return:
    """
    corr = get_corr(begin_station_value, end_station_value)
    if corr > corr_thres:
        return True
    else:
        return False
    
    
def check_next_station(begin_station, end_station, possible_trend, corr_thres=0.8):
    """
    看在现在时刻，根据当前的风速度，从begin_station传播到end_station是否可能
    :param begin_station:
    :param end_station:
    :param possible_trend: 由get_rise_trend得到的有上升趋势的点
    :param corr_thres： 相关系数的阈值
    :return:
    """
    # 先验证当前的风力风向传播到end_station的时间间隔
    time_window = calc_wind_time(begin_station, end_station)
    if not time_window:
        return False
    begin_time = begin_station['date_time']
    start_time = time_window[0]
    end_time = time_window[1]+1
    possible_arrive_time = [begin_time+i*3600 for i in range(start_time, end_time)]
    
    # 再验证在该时间窗口下，每个时刻end_station的污染物上升趋势与begin_station的相关系数，并选取最大相关系数的时刻
    max_corr = False
    for each_time in possible_arrive_time:
        if end_station in possible_trend[each_time]:
            corr = get_corr(begin_station['pollution'], possible_trend[each_time][end_station]['pollution'])
            if max_corr < corr:
                max_corr = corr
                arrive_time = each_time
    if max_corr < corr_thres:
        return False
    return arrive_time
    

def get_trajectory(begin_station, stations, possible_trend, center_stations, transfer_time=True ):
    """
    给出雾霾上升的起始站点，并计算出从该站点开始传播的雾霾的轨迹
    :param begin_station:
    :return:
    """
    # 从可能到的传播站点中找到符合要求的站点
    next_stations = defaultdict(dict)
    for next_station in stations[begin_station["name"]]['next_reasonable_station']:
        if not ((next_station in center_stations) and (begin_station['name'] in center_stations)):
            arrive_time = check_next_station(begin_station, next_station, possible_trend)
            if arrive_time:
                if next_station in center_stations:
                    if transfer_time:
                        next_stations[(next_station, timestamp_to_string(arrive_time))]
                    else:
                        next_stations[(next_station, arrive_time)]
                else:
                    next_station_info = {"date_time": arrive_time,
                                         "wind_direction": possible_trend[arrive_time][next_station]['wind_direction'],
                                         "wind_power": possible_trend[arrive_time][next_station]['wind_power'],
                                         "pollution": possible_trend[arrive_time][next_station]['pollution'],
                                         "angle": stations[next_station]['station_angle'],
                                         "distance": stations[next_station]['station_distance'],
                                         "name": next_station
                                         }
                    result = get_trajectory(next_station_info, stations, possible_trend, center_stations)
                    if result:
                        if transfer_time:
                            next_stations[(next_station, timestamp_to_string(arrive_time))] = result
                        else:
                            next_stations[(next_station, arrive_time)] = result
    if next_stations:
        return next_stations
    
    
class CalcTrajectory:
    
    def __init__(self, center_stations, time_step=5, pollution_increase=50, pollution_thres=100,
                 min_pollution_increase=30, min_pollution_thres=80):
        self.time_step = time_step
        self.pollution_increase = pollution_increase
        self.pollution_thres = pollution_thres
        self.min_pollution_increase = min_pollution_increase
        self.min_pollution_thres = min_pollution_thres
        self.center_stations = center_stations
        
    def begin(self, data):
        stations = data['stations']
        stations_info = data['stations_info']
        start_pollution_stations = get_rise_trend(stations_info, pollution_increase=self.pollution_increase, pollution_thres=self.pollution_thres)
        possible_pollution_stations = get_rise_trend(stations_info, pollution_increase=self.min_pollution_increase, pollution_thres=self.min_pollution_thres)
        trajectory_result = defaultdict(dict)
        for start_time in start_pollution_stations:
            for station in start_pollution_stations[start_time]:
                begin_station_info = {"date_time": start_time,
                                      "wind_direction": start_pollution_stations[start_time][station]['wind_direction'],
                                      "wind_power": start_pollution_stations[start_time][station]['wind_power'],
                                      "pollution": start_pollution_stations[start_time][station]['pollution'],
                                      "angle": stations[station]['station_angle'],
                                      "name": station,
                                      "distance": stations[station]['station_distance']
                                     }
                result = get_trajectory(begin_station_info, stations, possible_pollution_stations, self.center_stations)
                if result:
                    trajectory_result[timestamp_to_string(start_time)][station] = result
        return trajectory_result


if __name__ == '__main__':
    # with open('../utils/train_data.pickle', 'rb') as f:
    #     data = pickle.load(f)
    # get_result = CalcTrajectory(chengdu_stations)
    # result = get_result.begin(data)
    # with open('../results/result.pickle', 'wb') as f:
    #     pickle.dump(result, f)
    
    with open('../results/result.pickle', 'rb') as f:
        result = pickle.load(f)
    result
