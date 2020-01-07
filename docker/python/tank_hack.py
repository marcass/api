# tank hack
from collections import deque
from numpy import median

# incoming: {'site': 'rob_tanks', 'value': 'PY;6;R;3.94;'}
# formated: data = {'measurement': 'tablename', 'tags':{'type':'meastype', 'sensorID':'sensor name', 'site': 'thissite'}, 'value':value}
# tank info
tanks_dict = {
    '1':{'name':'top', 'min_dist': 45, 'max_dist': 370},
    '2':{'name':'noels', 'min_dist': 20, 'max_dist': 370},
    '3':{'name':'sals', 'min_dist': 27, 'max_dist': 370},
    '4':{'name':'main', 'min_dist': 45, 'max_dist': 370},
    '5':{'name':'bay', 'min_dist': 45, 'max_dist': 370},
    '6':{'name':'relay', 'min_dist': None, 'max_dist': None}
}

# set up buffer
buffer_by_name_dict = {}
# setup que circular buffer class
class Buffer:
    def __init__(self, name):
        global buffer_by_name_dict
        self.name = name
        self.water_buff = deque([],3)
        self.batt_buff = deque([],3)
        buffer_by_name_dict[self.name] = self
    def filtered_water(self, val):
        self.water_buff.append(val)
        return int(median(self.water_buff))
    def filtered_batt(self, val):
        self.batt_buff.append(val)
        return float(median(self.batt_buff))

def tank_data(data):
    global buffer_by_name_dict
    global tanks_dict
    # print(data)
    # sens_array = ['top', 'noels', 'sals', 'main', 'bay', 'relay']
    try:
        info = data['value'].split(';')
        in_tank = tanks_dict[info[1]]['name']
    except:
        print("Could not parse data")
        return
    if in_tank not in buffer_by_name_dict:
        obj = in_tank
        obj = Buffer(in_tank)
    buff = buffer_by_name_dict[in_tank]
    try:
        dist = int(info[2])
        dist = buff.filtered_water(dist)
        # print(dist)
        if (dist < int(tanks_dict[info[1]]['min_dist'])) or (dist > int(tanks_dict[info[1]]['max_dist'])):
            print('Payload out of range')
            water_ret = None
        else:
            print('payload in range')
            dist = dist - int(tanks_dict[info[1]]['min_dist'])
            level = float(tanks_dict[info[1]]['max_dist'] - dist)/float(tanks_dict[info[1]]['max_dist']) * 100.0
            water_ret = {'tags': {'type':'water_level', 'sensorID':in_tank, 'site': data['site']}, 'value': level, 'measurement': 'tanks'}
    except:
        water_ret = None
    try:
        batt = float(info[3])
        batt = buff.filtered_batt(batt)
        if (batt == 0) or (batt > 5.0):
            batt_ret = None
        else:
            batt_ret = {'tags': {'type':'batt_level', 'sensorID':in_tank, 'site': data['site']}, 'value': batt, 'measurement': 'tanks'}
    except:
        print('battery exception')
        batt_ret = None
    return [water_ret, batt_ret]
