import requests, json
from datetime import datetime, date, timedelta

key = '68890bdccc15cdd8e9e1430ef0e3bfab' # key generated by openweathermaps, used to retrieve data
debug = 0 # variable used to allow debugging

def getC(loc):
	"""
	Fetches data of current weather of location loc....
	Returns json object...
	"""
	loc = loc.lower()
	try: # Here we check whether data is stored in file or not, if present and is not much older, it is returned otherwise if older, flag is set..
		flag = 0
		f = open("current", "r")
		counter = 0
		for line in f:
			j = json.loads(line)
			if j["list"][0]["name"].lower()==loc:
				flag = 1
				if ((datetime.utcnow()-datetime(1970, 1, 1)).total_seconds()-j["list"][0]["dt"])<=1000:
					if debug:
						print(json.dumps(j, indent=4))
					f.close()
					return j
				else:
					break
			counter += 1
		f.close()
	except:
		if debug:
			print("** Not able to open file **\n")
		pass
	base = 'http://api.openweathermap.org/data/2.5/find?q='
	ops = '&units=metric&appid='
	try:
		if debug:
			print("** Fetching Data **\n")
		r = requests.get(base+loc+ops+key) # request made to the server....
	except:
		raise
	j = json.loads(r.text)
	if debug:
		print(json.dumps(j, indent=4))
	try:
		j["list"][0]["name"] = loc
		if j['count']==0:
			raise ValueError("Server Error")
	except:
		raise ValueError("Server Error")
	if j['cod']!='200':
		raise Exception("Not a valid Location")
		
	if flag:
		# flag is set, so previous data is modified and written to the file....
		if debug:
			print(json.dumps(j, indent=4))
			print("** Previous data found but it was very old **\n")
			print("** Counter ** ", counter)
		try:
			f = open("current", "r")
			lst = f.readlines()
			f.close()
			lst[counter] = str(json.dumps(j)+"\n")
			f = open("current", "w")
			f.writelines(lst)
			f.close()
		except:
			if debug:
				print("** Not able to open file. flag is set. **")
	else:
		# No previous data was found, so new data is written at the end....
		if debug:
			print(json.dumps(j, indent=4))
			print("** Previous data was not found **\n")
		try:
			f = open("current", "a")
			f.write(json.dumps(j)+"\n")
			f.close()
		except:
			if debug:
				print("** Not able to open file. flag is not set. **")
	return j

def getD(loc):
	"""
	Fetches data of next 4 day weather of location loc....
	Returns json object...
	"""
	loc = loc.lower()
	try: # Here we check whether data is stored in file or not, if present and is not much older, it is returned otherwise if older, flag is set..
		flag = 0
		f = open("data", "r")
		counter = 0
		for line in f:
			j = json.loads(line)
			if j["city"]["name"].lower()==loc:
				flag = 1
				today = date.today().isoformat()
				if today==j["list"][0]["dt_txt"].split()[0]:
					if debug:
						print("** Found in file **")
						print(json.dumps(j, indent=4))
					f.close()
					return j
				else:
					break
			counter += 1
		f.close()
	except:
		if debug:
			print("** Not able to open file **\n")
		pass
	base = 'http://api.openweathermap.org/data/2.5/forecast?q='
	ops = '&units=metric&appid='
	try:
		if debug:
			print("** Fetching Data **\n")
		r = requests.get(base+loc+ops+key) # request made to the server....
	except:
		raise
	j = json.loads(r.text)
	try:
		j["city"]["name"] = loc
		if j['cnt']==0:
			raise ValueError("Server Error")
	except:
		raise ValueError("Server Error")
	if j['cod']!='200':
		raise Exception("Not a valid Location")
	
	if flag:
		# flag is set, so previous data is modified and written to the file....
		if debug:
			print(json.dumps(j, indent=4))
			print("** Previous data found but it was very old **\n")
			print("** Counter ** ", counter)
		try:
			f = open("data", "r")
			lst = f.readlines()
			f.close()
			lst[counter] = str(json.dumps(j)+"\n")
			f = open("data", "w")
			f.writelines(lst)
			f.close()
		except:
			if debug:
				print("** Not able to open file. flag is set. **")
			pass
	else:
		# No previous data was found, so new data is written at the end....
		if debug:
			print(json.dumps(j, indent=4))
			print("** Previous data was not found **\n")
		try:
			f = open("data", "a")
			f.write(json.dumps(j)+"\n")
			f.close()
		except:
			if debug:
				print("** Not able to open file. flag is not set. **")
			pass
	return j
	
def get(loc):
	"""
	Used to get the weather details required for our project...
	Returns a dictionary from which details can be extracted easily...
	"""
	try:
		dct = {}
		cur = getC(loc)
		nxt = getD(loc)
		
		# Setting up dictionary...
		dct["name"] = cur["list"][0]["name"] # Name of loaction
		dct["today"] = {}
		dct["today"]["temp"] = cur["list"][0]["main"]["temp"] # Current temperature
		dct["today"]["max"] = dct["today"]["temp"] # Maximum Temperature
		dct["today"]["min"] = dct["today"]["temp"] # Minimum Temperature
		dct["today"]["desc"] = cur["list"][0]["weather"][0]["description"] # Description of current weather data
		dct["today"]["icon"] = cur["list"][0]["weather"][0]["icon"] # Icon Id
		
		today = date.today()
		d = today
		t = timedelta(1)
		for i in range(1, 7):
			d = d+t
			s = d.strftime("%a")
			dct[i] = {}
			dct[i]["day"] = s # Name of day
			dct[i]["max"] = '' # Maximum Temperature
			dct[i]["min"] = '' # Minimum Temperature
			dct[i]["icon"] = '' # Icon Id
		d = today

		counter = 0
		f = 1
		# Storing data in dictionary, by calculating max. and min. temperature....
		for i in nxt["list"]:
			if f:
				if d.isoformat()<i["dt_txt"].split()[0]:
					pass
				else:
					f=0
			elif d.isoformat()==i["dt_txt"].split()[0]:
				if d==today:
					x = dct['today']
				else:
					x = dct[counter]
				if x['max']=='':
					x['max'] = i["main"]["temp_max"]
					x['min'] = i['main']['temp_min']
				else:
					x['max'] = max(x['max'], i["main"]["temp_max"])
					x['min'] = min(x['min'], i['main']['temp_min'])
				if d!=today and 'd' in i['weather'][0]['icon']:
					x['icon'] = i['weather'][0]['icon']
			else:
				counter += 1
				d = d+t
				x = dct[counter]
				x['max'] = i["main"]["temp_max"]
				x['min'] = i['main']['temp_min']
				x['icon'] = i['weather'][0]['icon']
		
		return dct
	except:
		raise

def cities():
	"""
	Returns a list of valid locations... Used to validate the location entered by user and to give suggestions...
	"""
	f = open('city.list.json', 'r')
	lst = []
	for line in f:
		j = json.loads(line)
		lst.append(j['name']+','+j['country'])
	return lst

if __name__=="__main__":
	cities()
	loc = raw_input("Enter location: ")
	try:
		dct = get(loc)
		if dct['name'] == '':
			raise ValueError
		elif dct['name'].lower()!=loc.lower():
			print(loc+" not found. The closest match is:")
			print("Place: ", dct['name'])
			print("Temp: ", dct['today']['temp'])
		print("Min: ", dct['today']['min'])
		print("Max: ", dct['today']['max'])
		print("Icon id: ", dct['today']['icon'])
		print("Description: ", dct['today']['desc'])
		for i in range(1, 5):
			print("Day: ", dct[i]['day'])
			print("Max: ", dct[i]['max'])
			print("Min: ", dct[i]['min'])
			print("Icon id: ", dct[i]['icon'])
	except requests.exceptions.ConnectionError:
		print('Not connected')
	except:
		print('Not a valid location')
		raise
