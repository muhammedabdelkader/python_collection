import json, yaml 

class weather:
	def __init__(self,app_id=0,country='Stockholm'):
		if app_id:
			self.app_id = app_id
		self.country = country
	def set_app_id(self,app_id):
		self.app_id= app_id
	def get_app_id(self):
		return self.app_id
	def set_country(self,country='Stockholm'):
		self.country = country
	def get_country(self):
		return self.country
