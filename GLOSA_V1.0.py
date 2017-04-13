# coding: utf-8

# Program to demonstrate GLOSA
from openpyxl import Workbook
import random
import numpy as np
from math import exp, factorial


# global constants
#margin=6
#road_length_x=1000
#road_height_y=400
#road_x=9
#road_y=56
#t_light_x=850
#t_light_y=130
spat_range = 500
density = 10.0  #veh per mile
t_step = 0.1
test_dur = 120.0
sim_time = test_dur
amb_ph_t = 3.0
red_amb_ph_t = 2.0
stop_gap = 8.0
brake = 1.5
accel = 2.5
departure = 400
x_grid = 20.0
y_grid = 50.0
v_grid = 10.0
e_grid = 1.0
a = 170.0
b = 1.6
c = 0.37
m = 1500.0


# global variables
#road_length_m = 550.0
speed_limit_mph = 40.0
speed_limit_mps = speed_limit_mph / 0.6 * 1000 / 60 / 60
driver_var = 0.2
v2x_veh_mix = 1.0
t_light_cycle = 60.0
t_light_split = 0.5
#reset = 0
#save_plot = 0
approach = 1000
orphan_veh_data = []
orphan_ave_data = []
v2x_veh_data = []
v2x_ave_data = []
t_light_data = []
run_scene = 0
run_time = 0.0
start_time = 0.0
#sim_data = []
orphan_vehs = []
v2x_vehs = []
veh_num = 0
plot_layout = 1
glosa_accel = 1
x_val_min = 0.0
x_val_max = sim_time / x_grid
y_val_min = -approach / y_grid
y_val_max = departure / y_grid
orphan_energy = 0.0
v2x_energy = 0.0
orphan_energy2 = 0.0
v2x_energy2 = 0.0
calc_progress = 0.0
data_calc = 0
#run_speed = 3.0


class sim_veh():
	def __init__(self, driver, spawn_time):
		self.driver = driver
		self.speed = speed_limit_mps * driver
		self.dist = -approach
		self.state = 'unspawned'
		self.spawn_t = spawn_time

def accel_rate(speed, driver):
	return 1.7 * exp(-0.04 * speed) * driver

def braking_dist(speed, driver):
	br_dist = 0.0
	while speed > 1.0:
		br_dist += speed * t_step
		speed -= brake * driver * t_step
	return br_dist

def stopping_gap(speed, driver):
	return stop_gap + speed * 1.5 * 1+((driver-1)*-1)
	
def hysteresis(speed, driver):
	return speed * 0.2 * 1+((driver-1)*-1)
	
#def m2p(x_m):
#	return t_light_x + x_m * t_light_x / road_length_m
		
def mps2mph(mps):
	return mps / 1000 * 0.6 * 3600
	
def mph2mps(mph):
	return mph / 0.6 * 1000 / 60 / 60
	
def savitzky_golay(y, window_size, order, deriv, rate):

	try:
		window_size = abs(int(window_size))
		order = abs(int(order))
	except ValueError, msg:
		raise ValueError("window_size and order have to be of type int")
	if window_size % 2 != 1 or window_size < 1:
		raise TypeError("window_size size must be a positive odd number")
	if window_size < order + 2:
		raise TypeError("window_size is too small for the polynomials order")
	order_range = range(order+1)
	half_window = (window_size -1) // 2
	# precompute coefficients
	b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
	m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
	# pad the signal at the extremes with
	# values taken from the signal itself
	firstvals = y[0] - abs( y[1:half_window+1][::-1] - y[0] )
	lastvals = y[-1] + abs(y[-half_window-1:-1][::-1] - y[-1])
	y = np.concatenate((firstvals, y, lastvals))
	return np.convolve( m[::-1], y, mode='valid')
	
def calculate():
	global orphan_veh_data
	global orphan_ave_data
	global v2x_veh_data
	global v2x_ave_data
	global t_light_data
	global orphan_vehs
	global v2x_vehs
	global sim_time
	global veh_num
	global x_val_max
	global orphan_energy
	global v2x_energy
	global orphan_energy2
	global v2x_energy2
	global data_calc
	
	print 'Calculating . . .'
	orphan_veh_data = []
	v2x_veh_data = []
	t_light_data = []
	orphan_vehs = []
	v2x_vehs = []
	spawn_period = round(1/(density*0.6)/(speed_limit_mps/1000),1)
	veh_num = int(test_dur // spawn_period +1)
	#calc_est = test_dur + (approach + departure) / speed_limit_mps
	print spawn_period, veh_num
	
	for i in range(0,veh_num):
		orphan_veh_data.append([])
		v2x_veh_data.append([])
	
	for i in range(0,veh_num):
		driver = random.gauss(1, driver_var/3)
		spawn = i * spawn_period
		veh = sim_veh(driver, spawn)
		orphan_vehs.append(veh)
		veh = sim_veh(driver, spawn)
		v2x_vehs.append(veh)
	veh_in_front = sim_veh(1,0)
	v2x_in_front = sim_veh(1,0)
	
	t = 0.0
	phase = 0.0
	t_light_state = 'red'
	orphan_in_sim = 0
	v2x_in_sim = 0
	
	while t < test_dur or orphan_in_sim > 0 or v2x_in_sim > 0 or (t-0.1) % x_grid != 0:
		
		if t_light_state == 'red':
			if phase <= t_light_cycle * t_light_split - red_amb_ph_t:
				t_light_data.append( [round(t, 1), round(t_light_cycle * t_light_split - phase, 1), round(t_light_cycle - phase, 1), 'red'] )
			else:
				t_light_state = 'red_amb'
		if t_light_state == 'red_amb':
			if phase <= t_light_cycle * t_light_split:
				t_light_data.append( [round(t, 1), round(t_light_cycle * t_light_split - phase, 1), round(t_light_cycle -  phase, 1), 'red_amb'] )
			else:
				t_light_state = 'grn'
		if t_light_state == 'grn':
			if phase <= t_light_cycle - amb_ph_t:
				t_light_data.append( [round(t, 1), round(t_light_cycle * (1 + t_light_split) - phase, 1), round(t_light_cycle - phase, 1), 'grn'] )
			else:
				t_light_state = 'amb'
		if t_light_state == 'amb':
			if phase <= t_light_cycle:
				t_light_data.append( [round(t, 1), round(t_light_cycle * (1 + t_light_split) - phase, 1), round(t_light_cycle - phase, 1), 'amb'] )
			else:
				t_light_state = 'red'
				t_light_data.append( [round(t, 1), round(t_light_cycle * (1 + t_light_split) - red_amb_ph_t - phase, 1), round(2 * t_light_cycle - phase, 1), 'red'] )
				phase -= t_light_cycle
		phase += t_step
	
		# calculate orphan vehicle sim data
		veh_pos = 0
		veh_in_front.state = 'despawned'
		veh_in_front.dist = departure
		veh_in_front.driver = 1.0
		veh_in_front.speed = speed_limit_mps
		
		for veh in list(orphan_vehs):
			
			cur_dist = veh.dist
			cur_speed = veh.speed
			# spawn vehicles if due
			if veh.state == 'unspawned' and t >= veh.spawn_t:
				veh.state = 'cruise'
				orphan_in_sim += 1
				#print 'spawn orphan', t, veh_pos, orphan_in_sim
		
			if veh.state != 'unspawned' and veh.state != 'despawned':
				accel = accel_rate(veh.speed, veh.driver)
				gap = stopping_gap(veh.speed, veh.driver)
				hys = hysteresis(veh.speed, veh.driver)
				b_dist = braking_dist(veh.speed, veh.driver)
				vif_b_dist = braking_dist(veh_in_front.speed, veh_in_front.driver)
				
				if veh.state == 'cruise':
					if veh_in_front.state == 'despawned':
							veh.speed += accel * veh.driver * t_step
							if veh.speed > speed_limit_mps * veh.driver:
								veh.speed = speed_limit_mps * veh.driver
					# check and control safe cruising headway if inside soft headway limit
					elif veh_in_front.state == 'cruise':
						# decel if inside safe braking limit
						if veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
							veh.speed -= brake * veh.driver * t_step
						elif veh.dist + b_dist + gap - vif_b_dist + hys > veh_in_front.dist:
							veh.speed -= (a + b * veh.speed + c * veh.speed**2) / m * t_step
						# accelerate to cruising speed if outside safe braking limit
						elif (veh.dist + b_dist + gap - vif_b_dist < veh_in_front.dist) and (veh.speed < speed_limit_mps * veh.driver):
							veh.speed += accel * veh.driver * t_step
							if veh.speed > speed_limit_mps * veh.driver:
								veh.speed = speed_limit_mps *  veh.driver
	
					# check safe braking distances
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.state = 'brake'
					if t_light_state == 'red' and veh.dist + b_dist + gap > 0 and veh.dist < 0:
						veh.state = 'brake'
					if t_light_state == 'amb' and veh.dist + b_dist + gap > 0 and veh.dist < 0 and -veh.dist / veh.speed > t_light_data[int(t*10)][2]:
						veh.state = 'brake'
	
				if veh.state == 'brake':
					# brake if inside safe braking distance
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.speed -= brake * veh.driver * t_step
						
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist - vif_b_dist > veh_in_front.dist:
						veh.speed -= brake * veh.driver * t_step
					
					#if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + hys - vif_b_dist < veh_in_front.dist:
						#veh.state = 'accel'
						
					# brake if approaching red or amber
					if (t_light_state == 'amb' or t_light_state == 'red') and veh.dist + b_dist + gap > 0:
						if veh.dist + b_dist < 0:
							veh.speed -= brake * veh.driver * t_step
						elif veh.dist < 0:
							veh.speed -= brake * 2 * veh.driver * t_step
						
					if t_light_state == 'grn' or t_light_state == 'red_amb':
						if veh_in_front.state == 'despawned':
							veh.state = 'accel'
						elif (veh_in_front.state == 'cruise') and (veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist):
							veh.state = 'accel'
						elif (veh_in_front.state == 'accel') and (veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist):
							veh.state = 'accel'
							
					if veh.speed <= 1:
						veh.speed = 0
						veh.state = 'stop'
				
				if (veh.state == 'stop' and (t_light_state == 'grn' or t_light_state == 'red_amb')) and (veh_in_front.state == 'accel' or veh_in_front.state == 'cruise' or veh_in_front.state == 'despawned'):
					veh.state = 'accel'
					
				if veh.state == 'accel':
					if veh_in_front.state =='despawned':
						veh.speed += accel * veh.driver * t_step
						
					#if veh_in_front.state == 'cruise' and veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist:
						#veh.speed += accel * veh.driver * t_step
						
					if veh_in_front.state == 'accel' or veh_in_front.state == 'cruise':
						if veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist:
							veh.speed += accel * veh.driver * t_step
						elif veh.dist + b_dist + gap - vif_b_dist + hys > veh_in_front.dist:
							veh.speed -= (a + b * veh.speed + c * veh.speed**2) / m * t_step
						elif veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
							veh.speed -= brake * veh.driver * t_step
							veh.state = 'brake'
	
					if veh.speed > 0.8 * veh.driver * speed_limit_mps or veh.speed > 0.8 * veh_in_front.driver * speed_limit_mps:
						veh.state = 'cruise'
						
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.state = 'brake'
						veh.speed -= brake * veh.driver * t_step
					if t_light_state == 'red' and veh.dist + b_dist + gap > 0 and veh.dist < 0:
						veh.state = 'brake'
						veh.speed -= brake * veh.driver * t_step
					if t_light_state == 'amb' and veh.dist + b_dist + gap > 0 and veh.dist < 0 and -veh.dist / veh.speed > t_light_data[int(t*10)][2]:
						veh.state = 'brake'
						veh.speed -= brake * veh.driver * t_step
					
				veh.dist += veh.speed * t_step
				if veh.dist > departure:
					veh.dist = departure
					veh.state = 'despawned'
					orphan_in_sim -= 1
					#print 'despawn orphan', t, veh_pos, orphan_in_sim
					
			veh_in_front = veh
			
			orphan_veh_data[veh_pos].append([t, round(veh.speed,3), round(veh.dist,3), veh.state, 0, 0, 0])
			
			#print t, veh_pos
			veh_pos += 1
	
		# calculate v2x vehicle sim data
		veh_pos = 0
		veh_in_front.state = 'despawned'
		veh_in_front.dist = departure
		veh_in_front.driver = 1.0
		veh_in_front.speed = speed_limit_mps
		
		for veh in list(v2x_vehs):
			
			cur_dist = veh.dist
			cur_speed = veh.speed
		
			# spawn vehicles if due
			if veh.state == 'unspawned' and t >= veh.spawn_t:
				veh.state = 'cruise'
				v2x_in_sim += 1
				#print 'spawn v2x', t, veh_pos, v2x_in_sim
		
			if veh.state != 'unspawned' and veh.state != 'despawned':
				accel = accel_rate(veh.speed, veh.driver)
				gap = stopping_gap(veh.speed, veh.driver)
				hys = hysteresis(veh.speed, veh.driver)
				b_dist = braking_dist(veh.speed, veh.driver)
				vif_b_dist = braking_dist(veh_in_front.speed, veh_in_front.driver)
				
				#if veh.state == 'cruise' and veh.dist > -spat_range and veh.dist < 0:
					#veh.state = 'glosa'
					
				if veh.state == 'cruise':
					if veh.dist > -spat_range and veh.dist < 0:
						veh.state = 'glosa'
					elif veh_in_front.state == 'despawned':
							veh.speed += accel * veh.driver * t_step
							if veh.speed > speed_limit_mps * veh.driver:
								veh.speed = speed_limit_mps * veh.driver
					# check and control safe cruising headway if inside soft headway limit
					elif veh_in_front.state == 'cruise':
						# decel if inside safe braking limit
						if veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
							veh.speed -= brake * veh.driver * t_step
						elif veh.dist + b_dist + gap - vif_b_dist + hys > veh_in_front.dist:
							veh.speed -= (a + b * veh.speed + c * veh.speed**2) / m * veh.driver * t_step
						# accelerate to cruising speed if outside safe braking limit
						elif veh.dist + b_dist + gap - vif_b_dist < veh_in_front.dist and veh.speed < speed_limit_mps * veh.driver:
							veh.speed += accel / 3 * veh.driver * t_step
							if veh.speed > speed_limit_mps * veh.driver:
								veh.speed = speed_limit_mps *  veh.driver
	
					# check safe braking distances
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.state = 'brake'
					if t_light_state == 'red' and veh.dist + b_dist + gap > 0 and veh.dist < 0:
						veh.state = 'brake'
					if t_light_state == 'amb' and veh.dist + b_dist + gap > 0 and veh.dist < 0 and -veh.dist / veh.speed > t_light_data[int(t*10)][2]:
						veh.state = 'brake'
	
				if veh.state == 'glosa':
					if t_light_state == 'grn' or t_light_state == 'amb':
						# check if can pass on this green phase
						if -veh.dist / speed_limit_mps < t_light_data[int(t*10)][2] - amb_ph_t:
							glosa_max = speed_limit_mps
							#glosa_min = -veh.dist / (t_light_data[int(t*10)][2] - amb_ph_t)
						else:
							glosa_max = -veh.dist / t_light_data[int(t*10)][1]
							#glosa_min = -veh.dist / (t_light_data[int(t*10)][2] - amb_ph_t + t_light_cycle)
					elif t_light_state == 'red' or t_light_state == 'red_amb':
						# check if can pass on upcoming green phase
						if -veh.dist / speed_limit_mps < t_light_data[int(t*10)][2] - amb_ph_t:
							glosa_max = -veh.dist / t_light_data[int(t*10)][1]
							#glosa_min = -veh.dist / (t_light_data[int(t*10)][2] - amb_ph_t)
						else:
							glosa_max = -veh.dist / (t_light_data[int(t*10)][1] + t_light_cycle)
							#glosa_min = -veh.dist / (t_light_data[int(t*10)][2] - amb_ph_t + t_light_cycle + t_light_cycle)
							
					if veh.dist >= 0:
						veh.state = 'accel'
					#elif veh_in_front.state == 'despawned':
						#veh.speed += accel * veh.driver * t_step
						#if veh.speed > speed_limit_mps * veh.driver:
							#veh.speed = speed_limit_mps * veh.driver
						
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.state = 'brake'
					elif t_light_state == 'amb' and veh.dist + b_dist + gap > 0 and veh.dist < 0 and -veh.dist / veh.speed > t_light_data[int(t*10)][2]:
						veh.state = 'brake'
					elif t_light_state == 'red' and veh.dist + b_dist + gap > 0 and veh.dist < 0 and -veh.dist / veh.speed < t_light_data[int(t*10)][1] - red_amb_ph_t:
						veh.state = 'brake'
						
					#print veh_pos, glosa_min, glosa_max
					# check and control safe cruising headway if inside soft headway limit
					elif veh_in_front.state == 'glosa' or veh_in_front.state == 'cruise' or veh_in_front.state == 'despawned' or veh_in_front.state == 'brake':
						# decel if inside safe braking limit
						if veh.speed > glosa_max:
							veh.speed -= brake * veh.driver * t_step
						elif veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
							veh.speed -= brake * veh.driver * t_step
						elif veh.dist + b_dist + gap - vif_b_dist + hys > veh_in_front.dist:
							veh.speed -= (a + b * veh.speed + c * veh.speed**2) / m * veh.driver * t_step
						
						# accelerate to glosa speed if outside safe braking limit
						
						else:
							veh.speed += accel / 3 * veh.driver * t_step
							if glosa_accel == 1 and veh.speed > max(speed_limit_mps * veh.driver, speed_limit_mps):
								veh.speed = max(speed_limit_mps * veh.driver, speed_limit_mps)
							if glosa_accel == 0 and  veh.speed > min(speed_limit_mps * veh.driver, speed_limit_mps):
								veh.speed = min(speed_limit_mps * veh.driver, speed_limit_mps)
								
						if veh.speed < mph2mps(10.0):
							veh.speed = mph2mps(10.0)
						
					# check safe braking distances
					#if veh_in_front.state == 'accel':
						#if veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
							#veh.state = 'brake'
						#elif veh.dist + b_dist + gap - vif_b_dist < veh_in_front.dist:
							#veh.state = 'accel'
				
				if veh.state == 'brake':
					# brake if inside safe braking distance
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.speed -= brake * veh.driver * t_step
						
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist - vif_b_dist > veh_in_front.dist:
						veh.speed -= brake * veh.driver * t_step
					
					#if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop' or veh_in_front.state == 'accel') and veh.dist + b_dist + hys - vif_b_dist < veh_in_front.dist:
						#veh.state = 'accel'
					
					# brake if approaching red or amber
					if (t_light_state == 'amb' or t_light_state == 'red') and veh.dist + b_dist + gap > 0:
						if veh.dist + b_dist < 0:
							veh.speed -= brake * veh.driver * t_step
						elif veh.dist < 0:
							veh.speed -= brake * 2 * veh.driver * t_step
						
					if t_light_state =='grn' or t_light_state == 'red_amb':
						if veh_in_front.state == 'despawned':
							veh.state = 'accel'
						elif (veh_in_front.state == 'cruise') and (veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist):
							veh.state = 'accel'
						elif (veh_in_front.state == 'accel') and (veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist):
							veh.state = 'accel'
							
					if veh.speed <= 1:
						veh.speed = 0
						veh.state = 'stop'
				
				if (veh.state == 'stop' and (t_light_state == 'grn' or t_light_state == 'red_amb')) and (veh_in_front.state == 'accel' or veh_in_front.state == 'cruise' or veh_in_front.state == 'despawned'):
					veh.state = 'accel'
					
				if veh.state == 'accel':
					if veh_in_front.state =='despawned':
						veh.speed += accel * veh.driver * t_step
							
					#if (veh_in_front.state == 'cruise' or veh_in_front.state == 'glosa') and veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist:
						#veh.speed += accel * veh.driver * t_step
						
					if veh_in_front.state == 'accel' or veh_in_front.state == 'cruise' or veh_in_front.state == 'glosa':
						if veh.dist + gap + b_dist - vif_b_dist + hys < veh_in_front.dist:
							veh.speed += accel * veh.driver * t_step
						elif veh.dist + b_dist + gap - vif_b_dist + hys > veh_in_front.dist:
							veh.speed -= (a + b * veh.speed + c * veh.speed**2) / m * t_step
						elif veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
							veh.speed -= brake * veh.driver * t_step
							veh.state = 'brake'
	
					if veh.speed > 0.8 * veh.driver * speed_limit_mps or veh.speed > 0.8 * veh_in_front.driver * speed_limit_mps:
							veh.state = 'cruise'
						
					if (veh_in_front.state == 'brake' or veh_in_front.state == 'stop') and veh.dist + b_dist + gap - vif_b_dist > veh_in_front.dist:
						veh.state = 'brake'
						veh.speed -= brake * veh.driver * t_step
					if t_light_state == 'red' and veh.dist + b_dist + gap > 0 and veh.dist < 0:
						veh.state = 'brake'
						veh.speed -= brake * veh.driver * t_step
					if t_light_state == 'amb' and veh.dist + b_dist + gap > 0 and veh.dist < 0 and -veh.dist / veh.speed > t_light_data[int(t*10)][2]:
						veh.state = 'brake'
						veh.speed -= brake * veh.driver * t_step
				
				veh.dist += veh.speed * t_step
				if veh.dist > departure:
					veh.dist = departure
					veh.state ='despawned'
					v2x_in_sim -= 1
					#print 'despawn v2x', t, veh_pos, v2x_in_sim
					
			veh_in_front = veh
			
			v2x_veh_data[veh_pos].append([t, round(veh.speed,3), round(veh.dist,3), veh.state, 0, 0, 0])
			
			#print t, veh_pos
			veh_pos += 1
		
		t += t_step
		#print veh_in_sim
		t = round(t,1)
		#v['progress_label'].text = str(int(t))+'s'
		#print 'Calculating . . . ' + str(int(t)) + 's'
	sim_time = t - t_step
	#print sim_time
	x_val_max = round(sim_time / x_grid, 1)
	data_calc = 1
	print 'Summarising . . .'
	
	#orphan_vel_sum = 0.0
	#v2x_vel_sum = 0.0
	#orphan_energy_sum = 0.0
	#v2x_energy_sum = 0.0
	for k in range(-approach, departure + 1, 1):
		orphan_ave_data.append([k, 0, 0])
		v2x_ave_data.append([k, 0, 0])
		orphan_ave_data[k + approach][0] = k
		v2x_ave_data[k + approach][0] = k
	
	for v in range(0, veh_num):
		filter_in = np.zeros(int(sim_time * 10) + 1)
		for i in range (0, int(sim_time * 10)):
			filter_in[i] = orphan_veh_data[v][i][1]
		filter_out = savitzky_golay(filter_in, 51, 9, 0, 1)
		for i in range (0, int(sim_time * 10)):
			orphan_veh_data[v][i][4] = filter_out[i]
			
		for i in range (0, int(sim_time * 10)):
			filter_in[i] = v2x_veh_data[v][i][1]
		filter_out = savitzky_golay(filter_in, 51, 9, 0, 1)
		for i in range (0, int(sim_time * 10)):
			v2x_veh_data[v][i][4] = filter_out[i]
			
		#Smooth velocity as moving average of 15 points
		
		#Calculate first 7 points 
		#orphan_veh_data[v][0][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1]) / 8
		#orphan_veh_data[v][1][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1] + orphan_veh_data[v][8][1]) / 9
		#orphan_veh_data[v][2][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1] + orphan_veh_data[v][8][1] + orphan_veh_data[v][9][1]) / 10
		#orphan_veh_data[v][3][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1] + orphan_veh_data[v][8][1] + orphan_veh_data[v][9][1] + orphan_veh_data[v][10][1]) / 11
		#orphan_veh_data[v][4][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1] + orphan_veh_data[v][8][1]+ orphan_veh_data[v][9][1] + orphan_veh_data[v][10][1] + orphan_veh_data[v][11][1]) / 12
		#orphan_veh_data[v][5][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1] + orphan_veh_data[v][8][1]+ orphan_veh_data[v][9][1] + orphan_veh_data[v][10][1] + orphan_veh_data[v][11][1] + orphan_veh_data[v][12][1]) / 13
		#orphan_veh_data[v][6][4] = (orphan_veh_data[v][0][1] + orphan_veh_data[v][1][1] + orphan_veh_data[v][2][1] + orphan_veh_data[v][3][1] + orphan_veh_data[v][4][1] + orphan_veh_data[v][5][1] + orphan_veh_data[v][6][1] + orphan_veh_data[v][7][1] + orphan_veh_data[v][8][1]+ orphan_veh_data[v][9][1] + orphan_veh_data[v][10][1] + orphan_veh_data[v][11][1] + orphan_veh_data[v][12][1] + orphan_veh_data[v][13][1]) / 14
		#v2x_veh_data[v][0][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] +  + v2x_veh_data[v][7][1]) / 8
		#v2x_veh_data[v][1][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] + v2x_veh_data[v][7][1] + v2x_veh_data[v][8][1]) / 9
		#v2x_veh_data[v][2][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] + v2x_veh_data[v][7][1] + v2x_veh_data[v][8][1] + v2x_veh_data[v][9][1]) / 10
		#v2x_veh_data[v][3][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] + v2x_veh_data[v][7][1] + v2x_veh_data[v][8][1] + v2x_veh_data[v][9][1] + v2x_veh_data[v][10][1]) / 11
		#v2x_veh_data[v][4][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] + v2x_veh_data[v][7][1] + v2x_veh_data[v][8][1] + v2x_veh_data[v][9][1] + v2x_veh_data[v][10][1] + v2x_veh_data[v][11][1]) / 12
		#v2x_veh_data[v][5][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] + v2x_veh_data[v][7][1] + v2x_veh_data[v][8][1] + v2x_veh_data[v][9][1] + v2x_veh_data[v][10][1] + v2x_veh_data[v][11][1] + v2x_veh_data[v][12][1]) / 13
		#v2x_veh_data[v][6][4] = (v2x_veh_data[v][0][1] + v2x_veh_data[v][1][1] + v2x_veh_data[v][2][1] + v2x_veh_data[v][3][1] + v2x_veh_data[v][4][1] + v2x_veh_data[v][5][1] + v2x_veh_data[v][6][1] + v2x_veh_data[v][7][1] + v2x_veh_data[v][8][1] + v2x_veh_data[v][9][1] + v2x_veh_data[v][10][1] + v2x_veh_data[v][11][1] + v2x_veh_data[v][12][1] + v2x_veh_data[v][13][1]) / 14
		
		#Loop for points 8 thru 8th from end
		#for i in range(7, int(sim_time*10)-7):
			#orphan_veh_data[v][i][4] = (orphan_veh_data[v][i-7][1] + orphan_veh_data[v][i-6][1] + orphan_veh_data[v][i-5][1] + orphan_veh_data[v][i-4][1] + orphan_veh_data[v][i-3][1] + orphan_veh_data[v][i-2][1] + orphan_veh_data[v][i-1][1] + orphan_veh_data[v][i][1] + orphan_veh_data[v][i+1][1] + orphan_veh_data[v][i+2][1] + orphan_veh_data[v][i+3][1] + orphan_veh_data[v][i+4][1] + orphan_veh_data[v][i+5][1] + orphan_veh_data[v][i+6][1] + orphan_veh_data[v][i+7][1]) / 15
			#v2x_veh_data[v][i][4] = (v2x_veh_data[v][i-7][1] + v2x_veh_data[v][i-6][1] + v2x_veh_data[v][i-5][1] + v2x_veh_data[v][i-4][1] + v2x_veh_data[v][i-3][1] + v2x_veh_data[v][i-2][1] + v2x_veh_data[v][i-1][1] + v2x_veh_data[v][i][1] + v2x_veh_data[v][i+1][1] + v2x_veh_data[v][i+2][1] + v2x_veh_data[v][i+3][1] + v2x_veh_data[v][i+4][1] + v2x_veh_data[v][i+5][1] + v2x_veh_data[v][i+6][1] + v2x_veh_data[v][i+7][1]) / 15

		#Calculate last 7 points 			
		#orphan_veh_data[v][int(sim_time*10)][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] +  + orphan_veh_data[v][int(sim_time*10)-7][1]) / 8
		#orphan_veh_data[v][int(sim_time*10)-1][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] + orphan_veh_data[v][int(sim_time*10)-7][1] + orphan_veh_data[v][int(sim_time*10)-8][1]) / 9
		#orphan_veh_data[v][int(sim_time*10)-2][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] + orphan_veh_data[v][int(sim_time*10)-7][1] + orphan_veh_data[v][int(sim_time*10)-8][1] + orphan_veh_data[v][int(sim_time*10)-9][1]) / 10
		#orphan_veh_data[v][int(sim_time*10)-3][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] + orphan_veh_data[v][int(sim_time*10)-7][1] + orphan_veh_data[v][int(sim_time*10)-8][1] + orphan_veh_data[v][int(sim_time*10)-9][1] + orphan_veh_data[v][int(sim_time*10)-10][1]) / 11
		#orphan_veh_data[v][int(sim_time*10)-4][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] + orphan_veh_data[v][int(sim_time*10)-7][1] + orphan_veh_data[v][int(sim_time*10)-8][1] + orphan_veh_data[v][int(sim_time*10)-9][1] + orphan_veh_data[v][int(sim_time*10)-10][1] + orphan_veh_data[v][int(sim_time*10)-11][1]) / 12
		#orphan_veh_data[v][int(sim_time*10)-5][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] + orphan_veh_data[v][int(sim_time*10)-7][1] + orphan_veh_data[v][int(sim_time*10)-8][1] + orphan_veh_data[v][int(sim_time*10)-9][1] + orphan_veh_data[v][int(sim_time*10)-10][1] + orphan_veh_data[v][int(sim_time*10)-11][1] + orphan_veh_data[v][int(sim_time*10)-12][1]) / 13
		#orphan_veh_data[v][int(sim_time*10)-6][4] = (orphan_veh_data[v][int(sim_time*10)][1] + orphan_veh_data[v][int(sim_time*10)-1][1] + orphan_veh_data[v][int(sim_time*10)-2][1] + orphan_veh_data[v][int(sim_time*10)-3][1] + orphan_veh_data[v][int(sim_time*10)-4][1] + orphan_veh_data[v][int(sim_time*10)-5][1] + orphan_veh_data[v][int(sim_time*10)-6][1] + orphan_veh_data[v][int(sim_time*10)-7][1] + orphan_veh_data[v][int(sim_time*10)-8][1] + orphan_veh_data[v][int(sim_time*10)-9][1] + orphan_veh_data[v][int(sim_time*10)-10][1] + orphan_veh_data[v][int(sim_time*10)-11][1] + orphan_veh_data[v][int(sim_time*10)-12][1] + orphan_veh_data[v][int(sim_time*10)-13][1]) / 14
		#v2x_veh_data[v][int(sim_time*10)][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1]) / 8
		#v2x_veh_data[v][int(sim_time*10)-1][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1] + v2x_veh_data[v][int(sim_time*10)-8][1]) / 9
		#v2x_veh_data[v][int(sim_time*10)-2][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1] + v2x_veh_data[v][int(sim_time*10)-8][1] + v2x_veh_data[v][int(sim_time*10)-9][1]) / 10
		#v2x_veh_data[v][int(sim_time*10)-3][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1] + v2x_veh_data[v][int(sim_time*10)-8][1] + v2x_veh_data[v][int(sim_time*10)-9][1] + v2x_veh_data[v][int(sim_time*10)-10][1]) / 11
		#v2x_veh_data[v][int(sim_time*10)-4][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1] + v2x_veh_data[v][int(sim_time*10)-8][1] + v2x_veh_data[v][int(sim_time*10)-9][1] + v2x_veh_data[v][int(sim_time*10)-10][1] + v2x_veh_data[v][int(sim_time*10)-11][1]) / 12
		#v2x_veh_data[v][int(sim_time*10)-5][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1] + v2x_veh_data[v][int(sim_time*10)-8][1] + v2x_veh_data[v][int(sim_time*10)-9][1] + v2x_veh_data[v][int(sim_time*10)-10][1] + v2x_veh_data[v][int(sim_time*10)-11][1] + v2x_veh_data[v][int(sim_time*10)-12][1]) / 13
		#v2x_veh_data[v][int(sim_time*10)-6][4] = (v2x_veh_data[v][int(sim_time*10)][1] + v2x_veh_data[v][int(sim_time*10)-1][1] + v2x_veh_data[v][int(sim_time*10)-2][1] + v2x_veh_data[v][int(sim_time*10)-3][1] + v2x_veh_data[v][int(sim_time*10)-4][1] + v2x_veh_data[v][int(sim_time*10)-5][1] + v2x_veh_data[v][int(sim_time*10)-6][1] + v2x_veh_data[v][int(sim_time*10)-7][1] + v2x_veh_data[v][int(sim_time*10)-8][1] + v2x_veh_data[v][int(sim_time*10)-9][1] + v2x_veh_data[v][int(sim_time*10)-10][1] + v2x_veh_data[v][int(sim_time*10)-11][1] + v2x_veh_data[v][int(sim_time*10)-12][1] + v2x_veh_data[v][int(sim_time*10)-13][1]) / 14
		
		#Calculate power in kW
		for i in range(1, int(sim_time*10)):
			orphan_inertia_force = m * (orphan_veh_data[v][i][4] - orphan_veh_data[v][i-1][4]) / t_step
			v2x_inertia_force = m * (v2x_veh_data[v][i][4] - v2x_veh_data[v][i-1][4]) / t_step
			orphan_veh_data[v][i][5] = round((a + b * orphan_veh_data[v][i][4] + c * orphan_veh_data[v][i][4]**2 + orphan_inertia_force) * (orphan_veh_data[v][i][2] - orphan_veh_data[v][i-1][2]) / 100, 3)
			if orphan_veh_data[v][i][5] < 0.0:
				orphan_veh_data[v][i][5] = 0.000
			orphan_energy += orphan_veh_data[v][i][5] * 2.778 * 10**-5
			v2x_veh_data[v][i][5] = round((a + b * v2x_veh_data[v][i][4] + c * v2x_veh_data[v][i][4]**2 + v2x_inertia_force) * (v2x_veh_data[v][i][2] - v2x_veh_data[v][i-1][2]) / 100, 3)
			if v2x_veh_data[v][i][5] < 0.0:
				v2x_veh_data[v][i][5] = 0.000
			v2x_energy += v2x_veh_data[v][i][5] * 2.778 * 10**-5

	for v in range(0, veh_num):
		filter_in = np.zeros(int(sim_time * 10) + 1)
		for i in range (0, int(sim_time * 10)):
			filter_in[i] = orphan_veh_data[v][i][5]
		filter_out = savitzky_golay(filter_in, 201, 5, 0, 1)
		#filter_out = filter_in
		for i in range (0, int(sim_time * 10)):
			orphan_veh_data[v][i][6] = filter_out[i]
			
		for i in range (0, int(sim_time * 10)):
			filter_in[i] = v2x_veh_data[v][i][5]
		filter_out = savitzky_golay(filter_in, 201, 5, 0, 1)
		#filter_out = filter_in
		for i in range (0, int(sim_time * 10)):
			v2x_veh_data[v][i][6] = filter_out[i]
		
		#Smooth power as moving average of 15 points
		#Calculate first 7 points 
		#orphan_veh_data[v][0][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5]) / 8
		#orphan_veh_data[v][1][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5] + orphan_veh_data[v][8][5]) / 9
		#orphan_veh_data[v][2][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5] + orphan_veh_data[v][8][5] + orphan_veh_data[v][9][5]) / 10
		#orphan_veh_data[v][3][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5] + orphan_veh_data[v][8][5] + orphan_veh_data[v][9][5] + orphan_veh_data[v][10][5]) / 11
		#orphan_veh_data[v][4][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5] + orphan_veh_data[v][8][5] + orphan_veh_data[v][9][5] + orphan_veh_data[v][10][5] + orphan_veh_data[v][11][5]) / 12
		#orphan_veh_data[v][5][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5] + orphan_veh_data[v][8][5] + orphan_veh_data[v][9][5] + orphan_veh_data[v][10][5] + orphan_veh_data[v][11][5] + orphan_veh_data[v][12][5]) / 13
		#orphan_veh_data[v][6][6] = (orphan_veh_data[v][0][5] + orphan_veh_data[v][1][5] + orphan_veh_data[v][2][5] + orphan_veh_data[v][3][5] + orphan_veh_data[v][4][5] + orphan_veh_data[v][5][5] + orphan_veh_data[v][6][5] + orphan_veh_data[v][7][5] + orphan_veh_data[v][8][5] + orphan_veh_data[v][9][5] + orphan_veh_data[v][10][5] + orphan_veh_data[v][11][5] + orphan_veh_data[v][12][5] + orphan_veh_data[v][13][5]) / 14
		#v2x_veh_data[v][0][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5]) / 8
		#v2x_veh_data[v][1][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5] + v2x_veh_data[v][8][5]) / 9
		#v2x_veh_data[v][2][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5] + v2x_veh_data[v][8][5] + v2x_veh_data[v][9][5]) / 10
		#v2x_veh_data[v][3][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5] + v2x_veh_data[v][8][5] + v2x_veh_data[v][9][5] + v2x_veh_data[v][10][5]) / 11
		#v2x_veh_data[v][4][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5] + v2x_veh_data[v][8][5] + v2x_veh_data[v][9][5] + v2x_veh_data[v][10][5] + v2x_veh_data[v][11][5]) / 12
		#v2x_veh_data[v][5][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5] + v2x_veh_data[v][8][5] + v2x_veh_data[v][9][5] + v2x_veh_data[v][10][5] + v2x_veh_data[v][11][5] + v2x_veh_data[v][12][5]) / 13
		#v2x_veh_data[v][6][6] = (v2x_veh_data[v][0][5] + v2x_veh_data[v][1][5] + v2x_veh_data[v][2][5] + v2x_veh_data[v][3][5] + v2x_veh_data[v][4][5] + v2x_veh_data[v][5][5] + v2x_veh_data[v][6][5] + v2x_veh_data[v][7][5] + v2x_veh_data[v][8][5] + v2x_veh_data[v][9][5] + v2x_veh_data[v][10][5] + v2x_veh_data[v][11][5] + v2x_veh_data[v][12][5] + v2x_veh_data[v][13][5]) / 14
		
		#Loop for points 8 thru 8th from end
		#for i in range(7, int(sim_time*10)-7):
			#orphan_veh_data[v][i][6] = round((orphan_veh_data[v][i-7][5] + orphan_veh_data[v][i-6][5] + orphan_veh_data[v][i-5][5] + orphan_veh_data[v][i-4][5] + orphan_veh_data[v][i-3][5] + orphan_veh_data[v][i-2][5] + orphan_veh_data[v][i-1][5] + orphan_veh_data[v][i][5] + orphan_veh_data[v][i+1][5] + orphan_veh_data[v][i+2][5] + orphan_veh_data[v][i+3][5] + orphan_veh_data[v][i+4][5] + orphan_veh_data[v][i+5][5] + orphan_veh_data[v][i+6][5] + orphan_veh_data[v][i+7][5]) / 15, 3)
			#orphan_energy2 += orphan_veh_data[v][i][6] / 36000
			#v2x_veh_data[v][i][6] = round((v2x_veh_data[v][i-7][5] + v2x_veh_data[v][i-6][5] + v2x_veh_data[v][i-5][5] + v2x_veh_data[v][i-4][5] + v2x_veh_data[v][i-3][5] + v2x_veh_data[v][i-2][5] + v2x_veh_data[v][i-1][5] + v2x_veh_data[v][i][5] + v2x_veh_data[v][i+1][5] + v2x_veh_data[v][i+2][5] + v2x_veh_data[v][i+3][5] + v2x_veh_data[v][i+4][5] + v2x_veh_data[v][i+5][5] + v2x_veh_data[v][i+6][5] + v2x_veh_data[v][i+7][5]) / 15, 3)
			#v2x_energy2 += v2x_veh_data[v][i][6] / 36000
	
		#orphan_veh_data[v][int(sim_time*10)][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5]) / 8
		#orphan_veh_data[v][int(sim_time*10)-1][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5] + orphan_veh_data[v][int(sim_time*10)-8][5]) / 9
		#orphan_veh_data[v][int(sim_time*10)-2][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5] + orphan_veh_data[v][int(sim_time*10)-8][5] + orphan_veh_data[v][int(sim_time*10)-9][5]) / 10
		#orphan_veh_data[v][int(sim_time*10)-3][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5] + orphan_veh_data[v][int(sim_time*10)-8][5] + orphan_veh_data[v][int(sim_time*10)-9][5] + orphan_veh_data[v][int(sim_time*10)-10][5]) / 11
		#orphan_veh_data[v][int(sim_time*10)-4][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5] + orphan_veh_data[v][int(sim_time*10)-8][5] + orphan_veh_data[v][int(sim_time*10)-9][5] + orphan_veh_data[v][int(sim_time*10)-10][5] + orphan_veh_data[v][int(sim_time*10)-11][5]) / 12
		#orphan_veh_data[v][int(sim_time*10)-5][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5] + orphan_veh_data[v][int(sim_time*10)-8][5] + orphan_veh_data[v][int(sim_time*10)-9][5] + orphan_veh_data[v][int(sim_time*10)-10][5] + orphan_veh_data[v][int(sim_time*10)-11][5] + orphan_veh_data[v][int(sim_time*10)-12][5]) / 13
		#orphan_veh_data[v][int(sim_time*10)-6][6] = (orphan_veh_data[v][int(sim_time*10)][5] + orphan_veh_data[v][int(sim_time*10)-1][5] + orphan_veh_data[v][int(sim_time*10)-2][5] + orphan_veh_data[v][int(sim_time*10)-3][5] + orphan_veh_data[v][int(sim_time*10)-4][5] + orphan_veh_data[v][int(sim_time*10)-5][5] + orphan_veh_data[v][int(sim_time*10)-6][5] + orphan_veh_data[v][int(sim_time*10)-7][5] + orphan_veh_data[v][int(sim_time*10)-8][5] + orphan_veh_data[v][int(sim_time*10)-9][5] + orphan_veh_data[v][int(sim_time*10)-10][5] + orphan_veh_data[v][int(sim_time*10)-11][5] + orphan_veh_data[v][int(sim_time*10)-12][5] + orphan_veh_data[v][int(sim_time*10)-13][5]) / 14
		#v2x_veh_data[v][int(sim_time*10)][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5]) / 8
		#v2x_veh_data[v][int(sim_time*10)-1][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5] + v2x_veh_data[v][int(sim_time*10)-8][5]) / 9
		#v2x_veh_data[v][int(sim_time*10)-2][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5] + v2x_veh_data[v][int(sim_time*10)-8][5] + v2x_veh_data[v][int(sim_time*10)-9][5]) / 10
		#v2x_veh_data[v][int(sim_time*10)-3][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5] + v2x_veh_data[v][int(sim_time*10)-8][5] + v2x_veh_data[v][int(sim_time*10)-9][5] + v2x_veh_data[v][int(sim_time*10)-10][5]) / 11
		#v2x_veh_data[v][int(sim_time*10)-4][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5] + v2x_veh_data[v][int(sim_time*10)-8][5] + v2x_veh_data[v][int(sim_time*10)-9][5] + v2x_veh_data[v][int(sim_time*10)-10][5] + v2x_veh_data[v][int(sim_time*10)-11][5]) / 12
		#v2x_veh_data[v][int(sim_time*10)-5][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5] + v2x_veh_data[v][int(sim_time*10)-8][5] + v2x_veh_data[v][int(sim_time*10)-9][5] + v2x_veh_data[v][int(sim_time*10)-10][5] + v2x_veh_data[v][int(sim_time*10)-11][5] + v2x_veh_data[v][int(sim_time*10)-12][5]) / 13
		#v2x_veh_data[v][int(sim_time*10)-6][6] = (v2x_veh_data[v][int(sim_time*10)][5] + v2x_veh_data[v][int(sim_time*10)-1][5] + v2x_veh_data[v][int(sim_time*10)-2][5] + v2x_veh_data[v][int(sim_time*10)-3][5] + v2x_veh_data[v][int(sim_time*10)-4][5] + v2x_veh_data[v][int(sim_time*10)-5][5] + v2x_veh_data[v][int(sim_time*10)-6][5] + v2x_veh_data[v][int(sim_time*10)-7][5] + v2x_veh_data[v][int(sim_time*10)-8][5] + v2x_veh_data[v][int(sim_time*10)-9][5] + v2x_veh_data[v][int(sim_time*10)-10][5] + v2x_veh_data[v][int(sim_time*10)-11][5] + v2x_veh_data[v][int(sim_time*10)-12][5] + v2x_veh_data[v][int(sim_time*10)-13][5]) / 14		
			
		i = 0
		l = 0	
		for k in range(-approach, departure, 1):
			#print v, k, orphan_veh_data[v][i][2]
			while orphan_veh_data[v][i][2] <= k:
				i += 1
			j = (k - orphan_veh_data[v][i-1][2]) / (orphan_veh_data[v][i][2] - orphan_veh_data[v][i-1][2])
			#print j
			orphan_ave_data[k + approach][1] += (orphan_veh_data[v][i-1][4] + (orphan_veh_data[v][i][4] - orphan_veh_data[v][i-1][4]) * j)
			orphan_ave_data[k + approach][2] += (orphan_veh_data[v][i-1][6] + (orphan_veh_data[v][i][6] - orphan_veh_data[v][i-1][6]) * j)
			
			while v2x_veh_data[v][l][2] <= k:
				l += 1
			j = (k - v2x_veh_data[v][l-1][2]) / (v2x_veh_data[v][l][2] - v2x_veh_data[v][l-1][2])
			v2x_ave_data[k + approach][1] += (v2x_veh_data[v][l-1][4] + (v2x_veh_data[v][l][4] - v2x_veh_data[v][l-1][4]) * j)
			v2x_ave_data[k + approach][2] += (v2x_veh_data[v][l-1][6] + (v2x_veh_data[v][l][6] - v2x_veh_data[v][l-1][6]) * j)
		
	for k in range(-approach, departure, 1):
		orphan_ave_data[k + approach][1] = round(orphan_ave_data[k + approach][1] / veh_num, 3)
		orphan_ave_data[k + approach][2] = round(orphan_ave_data[k + approach][2] / veh_num, 3)
		v2x_ave_data[k + approach][1] = round(v2x_ave_data[k + approach][1] / veh_num, 3)
		v2x_ave_data[k + approach][2] = round(v2x_ave_data[k + approach][2] / veh_num, 3)
			
	print 'Calculation Complete'

calculate()

wb = Workbook()

dest_filename = 'glosa.xlsx'

ws1 = wb.active
ws1.title = "Run1"

for i in range (0, int(sim_time * 10)):
	data_element=[]
	data_element.append(t_light_data[i][3])
	data_element.append(t_light_data[i][0])
	for v in range(0, veh_num):
		data_element.append(orphan_veh_data[v][i][1])
		#data_element.append(orphan_veh_data[v][i][2])		# Distance
		#data_element.append(orphan_veh_data[v][i][3])
		#data_element.append(orphan_veh_data[v][i][4])
		#data_element.append(orphan_veh_data[v][i][5])
		#data_element.append(orphan_veh_data[v][i][6])
		data_element.append(v2x_veh_data[v][v][1])
		#data_element.append(v2x_veh_data[v][i][2])			# Distance
		#data_element.append(v2x_veh_data[v][i][3])
		#data_element.append(v2x_veh_data[v][i][4])
		#data_element.append(v2x_veh_data[v][i][5])
		#data_element.append(v2x_veh_data[v][i][6])
		
	ws1.append(data_element)

wb.save(filename = dest_filename)


