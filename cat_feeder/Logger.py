from time import time
import sys
import os
from datetime import datetime

class Logger():
	def __init__(self, innerLog=False, timerSampleN=20):
		self.st = time()
		self.timer_archive = []
		self.timerSampleN = timerSampleN
		self.reset(innerLog)
		self.cnt = 0
		
	def loading(self):
		cnt = self.cnt
		patterns = [
			[" /----",
			 "",
			 "",
			 ""],

			["    --\\",
			 "      |",
			 "",
			 ""],

			["      \\",
			 "      |",
			 "      |",
			 "     "],

			["",
			 "",
			 "      |",
			 "    --/"],

			["",
			 "",
			 "",
			 "  ----/"],
			
			["",
			 "",
			 " |",
			 " \\--"],
			
			["",
			 " |",
			 " |",
			 " \\"],
			
			[" /--",
			 " |",
			 "",
			 ""]
		]
		
		# cnt? ??? ???? ??
		if not 0 <= cnt <= 7:
			return None

		# ?? ??? ??? ???? ? ?? ??? ??? ??
		return "\n".join(patterns[cnt])
		
	def reset(self, innerLog):
		if (innerLog == False):
			sys.stdout = open(os.devnull, "w")
	
	def timer(self):
		et = time()
		ttt = et-self.st
		self.st = et
		
		self.timer_archive.append(ttt)
		if (len(self.timer_archive) > self.timerSampleN):
			self.timer_archive.pop(0)
		fps = 1/(sum(self.timer_archive)/len(self.timer_archive))
		return fps
			
	def __call__(self, ret):
		self.cnt = (self.cnt + 1)%8
		log = f'#### {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\tfps:{self.timer():.2f}\n'
		
		
		if (ret == 1):
			log += 'Fail to get sensor data.'
		else:
			cat = [cat['label'] for cat in ret['model']]
			log += f"\tDetect: {cat}\n"
			log += f"\tDistance: {ret['distance']}\n"
			log += f"\tWeight: {ret['weight']}\n"
			
		print(log, end='')
