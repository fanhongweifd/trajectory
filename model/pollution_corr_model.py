import numpy as np
import os
import sys
import pickle
from collections import defaultdict

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


def check_rise_trend(pollution_list ,pollution_increase, pollution_thres):
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
    assert time_step>=1, 'time_step must more than 1, but now is %s'%time_step
    stations_trend = defaultdict(dict)
    date_time = list(stations_info.keys())
    date_time.sort()
    for idx,begin_time in enumerate(date_time[0:-4]):
        continue_step = True
        for step_i in range(1,time_step):
            # 这里由于数据都是间隔一个小时，所以可以这样判断是否是连续数据。
            if step_i*3600 + begin_time != date_time[idx+step_i]:
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
                    if check_rise_trend(pollution_list,pollution_increase, pollution_thres):
                        stations_trend[begin_time][station] = dict(pollution=pollution_list, wind_power=wind_power_list,
                                                                   wind_direction=wind_direction_list)
    return stations_trend
                    
    



if __name__ == '__main__':

    with open('../utils/train_data.pickle', 'rb') as f:
        data = pickle.load(f)
    result = get_rise_trend(data['stations_info'])
    result