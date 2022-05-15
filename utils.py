import yaml
import time
import calendar
import os

def read_from_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f, yaml.FullLoader)

def write_to_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f)

def get_timestamp():
    return calendar.timegm(time.gmtime())

def get_data_time_boudaries_from(data_path):
    ym_list = os.listdir(os.path.normpath(data_path))
    ym_list.sort()
    start_ym, end_ym = ym_list[0], ym_list[len(ym_list) - 1]
    start_d_list = os.listdir(os.path.join(data_path, start_ym))
    end_d_list = os.listdir(os.path.join(data_path, end_ym))
    start_ymd = start_ym + '-' + start_d_list[0]
    end_ymd = end_ym + '-' + end_d_list[len(end_d_list) - 1]
    return start_ymd, end_ymd




