import cv2
import os
import subprocess
import time
from datetime import datetime
import json
from ppadb.client import Client as AdbClient


#client = AdbClient(host="127.0.0.1", port=5037)

def camera(ip):
    return
    device = None
    for d in client.devices():
        if d.serial == ip:
            device = d
            break
    
    if device is None:
        print('Fail to Connect ADB')
        return

    device.shell("input keyevent 27")
    print('adb camera')


            

class Recorder:
    def __init__(self, duration = 600, save_dir="cctv", temp_dir="cctv/temp", adb_ip = '192.168.0.1:8000'):
        self.save_dir = save_dir
        self.temp_dir = temp_dir
        self.frame_count = 0
        self.first_frame_time = None
        self.last_frame_time = None
        self.time_diffs = []
        
        self.adb_ip = adb_ip
        
        self.duration = duration

        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        # ?? ?? ???
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))

        self.filename = None
        self.reset()
        

    def reset(self):
        camera(self.adb_ip)
        self.archive = {
            'temperature': [],
            'humidity': [],
            'storage': [],
            'weight': [],
            'distance': [],
            'model': [],
            'meal': []
        }

    def __call__(self, datas):
        self.saveCamera(datas['frame'])
        self.archive['temperature'].append(datas['temperature'])
        self.archive['humidity'].append(datas['humidity'])
        self.archive['storage'].append(datas['storage'])
        self.archive['weight'].append(datas['weight'])
        self.archive['distance'].append(datas['distance'])
        self.archive['model'].append(datas['model'])
        self.archive['meal'].append(datas['meal'])

    def saveCamera(self, frame):
        now = time.time()

        if self.first_frame_time is None:
            self.first_frame_time = now
            self.last_frame_time = now
            first_dt = datetime.fromtimestamp(self.first_frame_time)
            first_time_str = first_dt.strftime("%Y%m%d_%H%M%S")

            self.filename = os.path.join(self.save_dir, f"{first_time_str}_{self.duration}s_cctv.mp4")

        else:
            self.time_diffs.append(now - self.last_frame_time)
            self.last_frame_time = now

        # ??? ??? 90? ??
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame_path = os.path.join(self.temp_dir, f"frame_{self.frame_count:06d}.jpg")
        cv2.imwrite(frame_path, rotated_frame)
        self.frame_count += 1

        # 10? ??? ?? ??
        if now - self.first_frame_time >= self.duration:
            self._make_video()
            self._clear_temp()

    def _make_video(self):
        print("Making video....")
        if not self.time_diffs:
            fps = 1
        else:
            avg_interval = sum(self.time_diffs) / len(self.time_diffs)
            fps = max(1, round(1 / avg_interval))

        first_dt = datetime.fromtimestamp(self.first_frame_time)
        first_time_str = first_dt.strftime("%Y%m%d_%H%M%S")
        duration = int(self.last_frame_time - self.first_frame_time)

        output_path = self.filename
        output_path_json = os.path.join(self.save_dir, f"{first_time_str}_{duration}s_data.json")

        # JSON ??
        with open(output_path_json, "w", encoding="utf-8") as f:
            json.dump(self.archive, f, ensure_ascii=False, indent=4)
        camera(self.adb_ip)

        # ?? ??
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", os.path.join(self.temp_dir, "frame_%06d.jpg"),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[Recorder] Saved video: {output_path}")

    def _clear_temp(self):
        for f in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, f))
        self.frame_count = 0
        self.first_frame_time = None
        self.last_frame_time = None
        self.time_diffs.clear()
