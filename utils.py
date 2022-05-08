import yaml
import time
import calendar

def read_from_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f, yaml.FullLoader)

def write_to_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f)

def get_timestamp():
    return calendar.timegm(time.gmtime())


