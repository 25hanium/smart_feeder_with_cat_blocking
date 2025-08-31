from picamera2 import Picamera2
import numpy as np
import serial
import time
import cv2

class Device():
	def __init__(self):
		
		self.arduino_port='/dev/ttyACM0'
		self.init_weihgt = 0
		self.fail_cnt = 0
		self.cmd = 0
		
		self.reset()
		self.calibration()
		
		if hasattr(self, "camera") and self.camera:
			self.camera.stop()
			self.camera.close()
		self.camera = Picamera2()
		self.camera.start()
		
	def reset(self):
		self.arduino_serial = serial.Serial(self.arduino_port, 115200, timeout=1)
		
	
	def calibration(self):
		while (True):
			ardu = self.callArduino()
			if (ardu == -1): continue
			else : temperature, humidity, storage, weight, distance = ardu
			
			self.init_weihgt = weight
			break
	
	def __call__(self, data):
		capture = self.camera.capture_array()
		capture = cv2.cvtColor(capture, cv2.COLOR_BGRA2RGB)
		data['frame'] = capture  # shape: (height, width, 3), dtype: uint8
		#return  data
		
		ardu = self.callArduino()
		if (ardu == -1): 
			self.fail_cnt += 1
			if (self.fail_cnt > 5):
				self.fail_cnt = 0
				self.reset()
			return 1
		else : temperature, humidity, storage, weight, distance = ardu
		
		data['temperature'] = temperature
		data['humidity'] = humidity
		data['storage'] = storage
		data['weight'] = int((weight - self.init_weihgt)/3215)
		data['distance'] = distance
		data['model'] = []
		
		return data

	def callArduino(self, cmd=0):
		if (cmd == 0): cmd = self.cmd
		self.arduino_serial.reset_input_buffer()
		self.arduino_serial.reset_output_buffer()

		if not (-3 <= cmd < 5):
			print(f'Wrong input. (cmd: {cmd})')
			return -1

		self.arduino_serial.write(f"{cmd}\n".encode())


		try:
			line = self.arduino_serial.readline()
			# ?????? ?? ? ?? ?????? ?????.
			if not line:
				print("Arduino timeout or no data received.")
				return -1

			decoded = line.decode(errors='replace').strip()
			values = decoded.split(',')
			if len(values) != 8:
				print("Wrong number of received data.")
				return -1

			status_val, temp_str, humid_str, ir1_str, ir2_str, ir3_str, weight_str, dist_str = values
			temperature = float(temp_str)
			humidity = float(humid_str)
			ir1 = int(ir1_str)
			ir2 = int(ir2_str)
			ir3 = int(ir3_str)
			weight = float(weight_str)
			distance = float(dist_str)
			storage = sum([(1 if ir < 100 else 0) for ir in [ir1, ir2, ir3]])

			return [temperature, humidity, storage, weight, distance]

		except Exception as e:
			print(f"Error reading Arduino: {e}")
			return -1
