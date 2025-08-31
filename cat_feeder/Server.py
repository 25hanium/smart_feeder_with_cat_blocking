import os, time, requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from datetime import time as ttt

class Server():
	def __init__(self):
		self.SERVER_BASE_URL='http://3.27.174.25:8080'
		self.API_KEY='hanium2025'   

		self.last_time = datetime.now().time()

		load_dotenv()
		self.BASE = self.SERVER_BASE_URL #os.getenv(self.SERVER_BASE_URL, "").rstrip("/")
		self.HEAD = {"X-API-Key": self.API_KEY} #os.getenv(self.API_KEY)}

	def __call__(self, data):
		self.report_left(data)

		if (data['meal'] is None): return
		if (data['meal']['weight'] < 1): return
		log = []
		log.append(data['meal']['tag_id'])
		log.append(data['meal']['weight'])
		log.append(int(data['meal']['feeding_amount']))
		log.append(int(data['meal']['left_amount']))
		log.append(data['meal']['timestamp_start'])
		log.append(data['meal']['timestamp_end'])
		log.append(data['meal']['file_path'])
		self.upload_feeding_log(*log)
		
		

	def report_left(self, data):
		now = datetime.now().time()
		midnight = ttt(0, 0, 0)
			
		if (now >= midnight >= self.last_time):
			self.report_left_amount(int(data['weight']))
		
		self.last_time = now
	
	def now_utc_iso(self):
		return datetime.now(timezone.utc).isoformat()

	def post(self, path, data, retries=3, timeout=5):
		url = f"{self.BASE}{path}"
		for i in range(retries):
			try:
				r = requests.post(url, headers=self.HEAD, json=data, timeout=timeout)
				r.raise_for_status()
				return r.json()
			except Exception as e:
				if i == retries - 1:
					raise
				time.sleep(2)

	def report_left_amount(self, left_g: int):
		print(f"/api/feeder-state\tleft_amount: {int(left_g)}")
		return
		return self.post("/api/feeder-state", {"left_amount": int(left_g)})

	def upload_feeding_log( self, 
		tag_id,
		weight_g: float,
		feeding_amount_g: int,
		left_amount_g: int,
		ts_start_iso: str | None = None,
		ts_end_iso: str | None = None,
		file_path: str | None = None,
	):
		
		payload = {
			"tag_id": tag_id,
			"weight": float(weight_g),              # ??? ?? ?
			"timestamp_start": ts_start_iso or now_utc_iso(),
			"timestamp_end": ts_end_iso or now_utc_iso(),
			"feeding_amount": int(feeding_amount_g),
			"left_amount": int(left_amount_g),
			"file_path": file_path,
		}
		print(payload)
		return
		return self.post("/api/feeding-logs", payload)
