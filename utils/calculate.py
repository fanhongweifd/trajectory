from math import *
import numpy as np


def merge_vector(value_list, angle_list):
    """
    合并向量列表，其中向量的值为value_list，向量的方向角为angle_list
    :param value_list:
    :param angle_list:
    :return:
    """
    assert len(value_list)==len(angle_list), "len(value_list)=%s, len(angle_list)=%s, must be equal."%(len(value_list),len(angle_list))
    angle_list = [angle*math.pi/180 for angle in angle_list]
    x_list = y_list = []
    for i in len(value_list):
        x_list.append(math.cos(angle_list[i])*value_list[i])
        y_list.append(math.sin(angle_list[i])*value_list[i])
    x = sum(x_list)
    y = sum(y_list)
    value = (x**2 + y**2)**0.5
    angle = math.atan2(y, x) * 180/math.pi
    if angle < 0:
        angle = angle+360
    return value, angle
    
    

def getDegree(latA, lonA, latB, lonB):
    """
    Args:
        point p1(latA, lonA)
        point p2(latB, lonB)
    Returns:
        bearing between the two GPS points,
        default: the basis of heading direction is north
    """
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360

    brng = -brng + 90
    if brng<0:
        brng = brng + 360
    return brng


def getDistance(latA, lonA, latB, lonB):
    ra = 6378140  # radius of equator: meter
    rb = 6356755  # radius of polar: meter
    flatten = (ra - rb) / ra  # Partial rate of the earth
    # change angle to radians
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    
    pA = atan(rb / ra * tan(radLatA))
    pB = atan(rb / ra * tan(radLatB))
    x = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(radLonA - radLonB))
    c1 = (sin(x) - x) * (sin(pA) + sin(pB)) ** 2 / cos(x / 2) ** 2
    c2 = (sin(x) + x) * (sin(pA) - sin(pB)) ** 2 / sin(x / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (x + dr)
    distance = distance/1000
    return distance


def sub_angle(angle_1, angle_2):
    """
    计算两个方向间的夹角：
    :param angle_1:
    :param angle_2:
    :return: angle
    """
    angle = abs(angle_1 - angle_2)
    if angle>180:
        angle = 360-angle
    return angle
    
    
def get_corr(list1, list2):
    """
    计算list1和list2的相关系数
    :return:
    """
    corr = np.corrcoef([list1, list2])
    corr = corr[0,1]
    return corr


class CalcData:
    
    def __init__(self, station_location=None):
        self.station_location = station_location
        
    def inter_distance(self, ori_location, station_location=None):
        assert not (station_location == None and self.station_location == None), "station_location is empty"
        if station_location==None:
            station_location = self.station_location
        for location in ori_location:
            longitude = ori_location[location]['longitude']
            latitude = ori_location[location]['latitude']
            if not 'distance' in ori_location[location]:
                ori_location[location]['distance'] = {}
            if not 'angle' in ori_location[location]:
                ori_location[location]['angle'] = {}
                
            for station_name, station_loc in station_location.items():
                distance = getDistance(latitude, longitude, station_loc['latitude'], station_loc['longitude'])
                angle = getDegree(latitude, longitude, station_loc['latitude'], station_loc['longitude'])
                ori_location[location]['distance'][station_name] = distance
                ori_location[location]['angle'][station_name] = angle
                if not 'min_distance' in ori_location[location]:
                    ori_location[location]['min_distance'] = distance
                if not 'min_distance_station' in ori_location[location]:
                    ori_location[location]['min_distance_station'] = station_name
                if ori_location[location]['min_distance'] > distance:
                    ori_location[location]['min_distance'] = distance
                    ori_location[location]['min_distance_station'] = station_name
                    
        return ori_location
    
    
class CalcAngleDistance():
    """
    计算从ori_station到station_location的距离和角度
    """
    
    def __init__(self, station_location):
        self.station_location = station_location
        
    def angle_distance(self,ori_station):
        angle = getDegree(ori_station['latitude'], ori_station['longitude'], self.station_location['latitude'], self.station_location['longitude'])
        distance = getDistance(ori_station['latitude'], ori_station['longitude'], self.station_location['latitude'], self.station_location['longitude'])
        return angle, distance
        
            
if __name__ == '__main__':
    print(getDegree(1, 0, 0, 0))
    
    
    
    



    
