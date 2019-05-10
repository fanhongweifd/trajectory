from model.pollution_corr_model import CalcTrajectory
import argparse
from data.public_parameter import chengdu_stations
import pickle

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('-t', '--time_step', type=int, default=5, help='continue pollution time step')
    parser.add_argument('--pollution_increase', type=float, default=50, help='pollution increase')
    parser.add_argument('--pollution_thres', type=float, default=100, help='pollution threshold')
    parser.add_argument('--min_pollution_increase', type=float, default=30, help='min pollution increase')
    parser.add_argument('--min_pollution_thres', type=float, default=80, help=' inner layer you want')
    parser.add_argument('--time_lag', type=float, default=24, help='max time lag between stations')
    parser.add_argument('--data_path', type=str, default='data/train_data.pickle', help='data path')
    parser.add_argument('--save_path', type=str, default='results/trajectory_result.pickle', help='data path')
    
    args = parser.parse_args()

    time_step = args.time_step
    pollution_increase = args.pollution_increase
    pollution_thres = args.pollution_thres
    min_pollution_increase = args.min_pollution_increase
    min_pollution_thres = args.min_pollution_thres
    center_stations = chengdu_stations
    time_lag = args.time_lag
    data_path = args.data_path
    save_path = args.save_path
    
    with open(data_path, 'rb') as f:
        data = pickle.load(f)

    get_result = CalcTrajectory(center_stations, time_step=time_step, pollution_increase=pollution_increase,
                                pollution_thres=pollution_thres, min_pollution_increase=min_pollution_increase,
                                min_pollution_thres=min_pollution_thres, time_lag=time_lag)
    result = get_result.begin(data)
    with open(save_path, 'wb') as f:
        pickle.dump(result, f)
        
    print('Finished.')