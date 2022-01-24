import ac
import acsys
# import configparser
import json
from os.path import exists

# CONFIG SETTINGS
title = 'Shift Combo'
base_dir = 'apps/python/'+title
car_dir = 'content/cars/'
data_dir = base_dir+'/data/'
data_ext = '.txt'
perfect_shift_range = 100
optimal_shift_range = 250
high_end_multiplier = 2
optimal = 0
rpm = 0
gear = 0

# INTERNAL DATA
update_interval = 0.01667
timer = 0

# LAMBDAS
getValidFileName = lambda f: ''.join(c for c in f if c in '-_() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
isInRange = lambda n, o, r, m: n >= o - r and n <= o + (r * m)

def log(msg):
	# Logging wrapper
	global title
	ac.log(title+': '+msg)

def acMain(ac_version):
	global title, optimal
	app = ac.newApp(title)
	ac.setSize(app, 308, 33)
	ac.setIconPosition(app, 0, -10000) # Get rid of the icon
	ac.setTitle(app, '') # Get rid of the title
	ac.drawBorder(app, 0)
	# For some reason, these 2 background functions can cause display issues,
	# so I'm just leaving them vanilla until I can figure it out
	ac.drawBackground(app, 1)
	ac.setBackgroundOpacity(app, background_opacity)
	optimal = getTorqueCurve()

def acUpdate(deltaT):
	global timer, update_interval, rpm, gear, optimal, optimal_shift_range, perfect_shift_range
	timer += deltaT
	
	# 60 times per second
	if (timer > update_interval):
		timer = 0
		new_gear = ac.getCarState(0, acsys.CS.Gear)
		if (new_gear > gear):
			gear = new_gear
			rpm = ac.getCarState(0, acsys.CS.RPM)
			if (isInRange(rpm, optimal, perfect_shift_range, 1)):
				# Perfect shift
				# Just a short range around the optimal because shifting at the exact number is
				# unlikely, and would be unfair 
				log('Perfect shift! '+gear+', '+rpm)
			else if (isInRange(rpm, optimal, optimal_shift_range, high_end_multiplier)):
				# Good shift
				# The optimal shift range is higher in the high side because someone is more likely to 
				# want to pass the optimal, then shift; also, torque generally decreases slower
				# after the optimal shift RPM than it rises prior to it, so a late shift is less
				# detrimental than an early shift
				log('Good shift! '+gear+', '+rpm)
			else:
				# Bad shift
				log('Bad shift! '+gear+', '+rpm)
			draw()

def draw():
	pass

def getTorqueCurve():
	# Load the ui/ui_car.json file for the current car, or a local file if it exists
	# Grab or create optimal shift RPM and max revs as a tuple
	global car_dir, data_dir, data_ext
	local_file = getValidFileName(data_dir+car+data_ext)
	if (exists(local_file)):
		f = open(local_file, 'r')
		line = f.readline()
		f.close()
		return line.split(';')
	else:
		car = ac.getCarName(0)
		orig_file = getValidFileName(car_dir+car+'/ui/ui_car.json')
		if (exists(orig_file)):
			torque = []
			f = open(orig_file, 'r')
			car_data = json.load(f)
			f.close()
			torque = analyzeTorqueCurve(car_data['torqueCurve'])
			with open(local_file, 'w') as f2:
				f.write(';'.join(map(str, torque)))
			return torque			
		else:
			log('No torque curve to be found!')
			return False

def analyzeTorqueCurve(torque):
	# Determine the RPM at which torque is highest
	# Return the optimal RPM and max RPMs as a tuple
	max_rev = torque[-1][0]
	adjusted = sorted(torque, key=lambda a: a[1])
	optimal = (
		adjusted[0][0],
		max_rev
	)
	return optimal

def acShutdown():
	pass