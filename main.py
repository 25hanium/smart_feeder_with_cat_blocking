import cat_feeder as cf
import time
import datetime
import os
import keyboard

adb_ip = '192.168.45.244:45069'

logger = cf.Logger(innerLog = True)

device = cf.Device()
recoder = cf.Recorder(adb_ip=adb_ip, duration=60*2)
detector = cf.Detector()
control = cf.Controller(device.callArduino, device)
server = cf.Server()

schedule = [datetime.time(6, 0, 0), datetime.time(12, 0, 0), datetime.time(18, 0, 0), datetime.time(0, 0, 0)]

control.ardu(-2)
#control.feedingTime = True

def main():
	ss = "#### Delay\n"
	st = time.time()
	data = {}
	data['frame'] = None
	data['temperature'] = None
	data['humidity'] = None
	data['storage'] = None
	data['weight'] = None
	data['distance'] = None
	data['model'] = []
	data['meal'] = None
	
	ret = device(data); ss += f'\tDevive: {time.time()-st:.2f}s\n'; st = time.time()
	data = detector(data); ss += f'\tdetector: {time.time()-st:.2f}s\n'; st = time.time()

	if (ret == 1): 
		recoder(data); ss += f'\trecoder: {time.time()-st:.2f}s\n'; st = time.time()
		return ret, ss
	else:
		data = ret
		
	data = control(data, recoder.filename, schedule); ss += f'\tcontrol: {time.time()-st:.2f}s\n'; st = time.time()
	recoder(data); ss += f'\trecoder: {time.time()-st:.2f}s\n'; st = time.time()
	server(data); ss += f'\tserver: {time.time()-st:.2f}s\n'; st = time.time()
	
	return data, ss
	
time.sleep(10)
while(True):
	ret, log = main()

	os.system('clear')	
	print(log)
	
	logger(ret)
	print(f"\tCSTATE: {control.cstate}")
	print(f"\tCSTATE: {control.freeze}")
	
	if (keyboard.is_pressed("q")):
		control.ardu(-2)
	elif (keyboard.is_pressed("w")):
		control.ardu(-1)
	elif (keyboard.is_pressed("e")):
		control.ardu(0)
	elif (keyboard.is_pressed("r")):
		control.ardu(1)
	elif (keyboard.is_pressed("t")):
		control.ardu(2)
	
	print("\nq: -2 |w: -1 |e: 0| r: 1 |t: 2")
	print(logger.loading())
	
