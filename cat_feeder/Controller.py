import time
import json
from importlib.resources import files
import datetime

profile_default_path = files('cat_feeder').joinpath('profile.json')


class Controller():
    def __init__(self, arduFunction, device, schedule=[], feed_cooldown=5, meal_threshold=5, cat_count=3):
        self.ardu = arduFunction
        self.device = device
        self.cstate = 'IDLE'
        self.nstate = 'IDLE'
        self.wait_time = 5
        self.st = 0
        self.meal = None
        self.profile = None
        self.last_time = datetime.datetime.now().time()
        self.feedingTime = False
        
        self.ban_id = [2]
        self.freeze = False
        self.freeze_st = 0
        self.freeze_time = 10
        
        self.threshold_distance =200
        self.reset()
        
    def feed(self, schedule):
        now = datetime.datetime.now().time()
        for sch in schedule:
            if (self.last_time <= sch <= now):
                self.feedingTime = True
        
        
    def start(self, cat_id, feading_amount):
        self.meal = {}
        self.meal['tag_id'] = cat_id
        self.meal['weight'] = 0
        self.meal['timestamp_start'] = time.time()
        self.meal['timestamp_end'] = time.time()
        self.meal['feeding_amount'] = feading_amount
        self.meal['left_amount'] = 0
        self.meal['file_path'] = None
        
    def end(self, remain_weight):
        self.meal['weight'] = self.meal['feeding_amount'] - remain_weight
        self.meal['timestamp_end'] = time.time()
        self.meal['left_amount'] = remain_weight
    
    def reset(self):
        self.cstate, self.nstate = 'IDLE', 'IDLE'
        with open(profile_default_path, 'r') as f:
            self.profile = json.load(f)
        
        
    def getNearCat(self, data):
        max_size = 0
        max_index = 0
        for i, cat in enumerate(data['model']):
            x1, y1, x2, y2 = cat['box']
            if (max_size < (x2-x1)*(y2-y1)):
                max_size = (x2-x1)*(y2-y1)
                max_index = i
                
        return data['model'][i]
            
    def __call__(self, data, filename, schedule):
        self.feed(schedule)
        data = self.FSM(data, filename)
        
        self.last_time = datetime.datetime.now().time()
        return data
        
    def FSM(self, data, filename):
        if (self.freeze == True):
            now = time.time()
            if (now - self.freeze_st > self.freeze_time):
                self.freeze = False
                self.ardu(-1)
                self.device.cmd = 0
            else:
                et = time.time()
                return data
        if (self.cstate != 'IDLE' and self.cstate != 'SAVE'):
            if (len(data['model']) != 0): 
                for cat in data['model']:
                    index = cat['label']
                    if (index in self.ban_id):
                        self.ardu(-2)
                        self.device.cmd = -2
                        self.freeze_st = time.time()
                        self.freeze = True
                        return data
        
        if (self.cstate == 'IDLE'):
            if (self.feedingTime == True):
                self.ardu(1)                   
                
                self.feedingTime = False
            
            if (len(data['model']) == 0): return data
            if (data['distance'] > self.threshold_distance*3): return data
            
            
            cat = self.getNearCat(data)
            index = cat['label']
            if (index in self.ban_id): return data
            self.ardu(1)
            
            cat_id = self.profile[index]['id']
            self.start(cat_id, 25)
            
            self.cstate = 'FEED'
        
        elif (self.cstate == 'FEED'):
            if (data['distance'] < self.threshold_distance): return data
            
            self.cstate = 'WAIT'
            self.st = time.time()
            
        elif (self.cstate == 'WAIT'):
            et = time.time()
            if (et-self.st < self.wait_time): return data
            if (data['distance'] < self.threshold_distance): 
                self.cstate = 'FEED'
                return data
            
            self.cstate = 'SAVE'
            self.ardu(-2)
        
        elif (self.cstate == 'SAVE'):
            self.meal['file_path'] = filename
            data['meal'] = self.meal
            self.cstate = 'IDLE'
        
        return data

