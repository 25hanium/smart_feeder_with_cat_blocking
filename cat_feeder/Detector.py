import torch
from ultralytics import YOLO
import cv2
from .model import getFaseNet
from torchvision import transforms
from importlib.resources import files
import numpy as np
import torch.nn.functional as F
import json

profile_default_path = files('cat_feeder').joinpath('profile.json')

class Detector():
	def __init__(self):
		self.model_yolo = YOLO("yolo11n.pt")
		
		self.model_cat = getFaseNet()
		self.transform = None
		self.profile = None
		self.profile_embedding = None
		
		self.reset()
	
	def reset(self):
		self.model_cat.eval()
		self.tramsform = transforms.Compose([
			transforms.ToPILImage(),
			transforms.Resize((224, 224)),  
			transforms.ToTensor(),
			transforms.Normalize(mean=[0.485, 0.456, 0.406],
								 std=[0.229, 0.224, 0.225]),
		])
		
		with open(profile_default_path, 'r') as f:
			self.profile = json.load(f)
			
			self.profile_embedding = torch.tensor([self.profile[key]['embedding'] for key in range(len(self.profile))])

	def process_batch(self, image_list):
		processed = [self.tramsform(img) for img in image_list]
		batch_tensor = torch.stack(processed) 
		return batch_tensor
		
	def __call__(self, datas):
		x = datas['frame']
		x = self.model_yolo(x, verbose=False)		
		x, datas = self.crop(x, datas)

		if (len(x) == 0): return datas

		x = self.catFacenet(x)
		x = x / np.linalg.norm(x, axis=1, keepdims=True)
		
		for i, embedding in enumerate(x):
			best = self.catClassification(embedding)
			
			datas['model'][i]['embedding'] = x.tolist()
			datas['model'][i]['label'] = int(best)
			
			if (datas['model'][i]['type'] == 'cat'):
				datas['model'][i]['label'] = 2
			else :
				datas['model'][i]['label'] = 3
		
		return datas
		
	def catFacenet(self, x):
		x = self.process_batch(x)
		with torch.no_grad():
			x = self.model_cat(x)
		
		return x 
			
	def catClassification(self, x):
		similarity = F.cosine_similarity(x, self.profile_embedding, dim=1)
		best = int(torch.argmax(similarity).cpu().item())
		
		return best

	def crop(self, results, datas):
		boxes = results[0].boxes
		crops = []

		for box in boxes:
			cls_id = int(box.cls[0]) 
			cls_name = self.model_yolo.names[cls_id]

			if cls_name == "cat" or cls_name == "teddy bear":  
				x1, y1, x2, y2 = box.xyxy[0].int().tolist()
				crop = datas['frame'][y1:y2, x1:x2]  
				crops.append(crop)
				
				datas['model'].append({'box': [x1, y1, x2, y2], 'type': cls_name})
				
		return crops, datas
