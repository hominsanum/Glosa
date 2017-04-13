# coding: utf-8

# Program to demonstrate GLOSA
import ui
import scene as S
#import scene_drawing
#import sound
import random
import numpy as np
from math import exp, factorial


# global constants
margin=6
road_length_x=1000
road_height_y=400
road_x=9
road_y=56
t_light_x=850
t_light_y=130
spat_range = 500
basic_veh = S.Texture('iow:location_32')
#v2x_veh = S.Texture('iow:wifi_24')
t_light_body = S.Texture('plf:Tile_DoorOpen_mid')
t_light_end = S.Texture('plf:Tile_DoorOpen_top')
light = S.Texture('shp:Circle')
density = 10.0  #veh per mile
t_step = 0.1
test_dur = 120.0
sim_time = test_dur
amb_ph_t = 3.0
red_amb_ph_t = 2.0
stop_gap = 8.0
brake = 1.5
#accel = 2.5
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
road_length_m = 550.0
speed_limit_mph = 40.0
speed_limit_mps = speed_limit_mph / 0.6 * 1000 / 60 / 60
driver_var = 0.2
v2x_veh_mix = 1.0
t_light_cycle = 60.0
t_light_split = 0.5
reset = 0
save_plot = 0
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
run_speed = 3.0


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
	
def m2p(x_m):
	return t_light_x + x_m * t_light_x / road_length_m
		
def mps2mph(mps):
	return mps / 1000 * 0.6 * 3600
	
def mph2mps(mph):
	return mph / 0.6 * 1000 / 60 / 60
	

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
	
	#print 'Calculating . . .'
	#v = self.superview
	orphan_veh_data = []
	v2x_veh_data = []
	t_light_data = []
	orphan_vehs = []
	v2x_vehs = []
	spawn_period = round(1/(density*0.6)/(speed_limit_mps/1000),1)
	veh_num = int(test_dur // spawn_period +1)
	#calc_est = test_dur + (approach + departure) / speed_limit_mps
	#print spawn_period, veh_num
	
	for i in range(0,veh_num):
		#print i
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
		print 'Calculating . . . ' + str(int(t)) + 's'
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

class Vehicle (S.SpriteNode):
	def __init__(self, **kwargs):
		S.SpriteNode.__init__(self, basic_veh, scale=1.5, **kwargs)
		text_font = ('Futura', 8)
		self.speed = speed_limit_mph
		self.distance = -approach
		self.state = 'cruise'
		self.state_marker = S.LabelNode(self.state, text_font, color='black', position=(0, 20, 1))
		self.add_child(self.state_marker)

		#self.dist_marker = S.LabelNode(str(int(self.distance))+'m', text_font, color='black', position=(0, 30, 1))
		#self.add_child(self.dist_marker)
		self.speed_marker = S.LabelNode(str(int(self.speed))+'mph', text_font, color='black', position=(0, 30, 1))
		self.add_child(self.speed_marker)
		self.pos_marker = S.LabelNode(str(0), text_font, color='black', position=(0, 40, 1))
		self.add_child(self.pos_marker)


class RoadView(ui.View):
	def __init__ (self, road_scn, parent = None):
		self.frame = (road_x, road_y, road_length_x+margin, road_height_y+margin)
		if parent:
			parent.add_subview(self)
		self.background_color = 'ivory'

		# road area
		self.scene_view = S.SceneView(frame = [margin/2, margin/2, road_length_x, road_height_y])
		self.scene_view.scene = road_scn
		self.add_subview(self.scene_view)
		
		# set ui
		v= self.superview
		#v['segmentedcontrol1'].selected_index = speed_limit_mph/10-3


class RoadScene(S.Scene):
	def __init__ (self):
		S.Scene.__init__(self)
		self.size = (road_length_x, road_height_y)
		self.orphan_vehs = []
		self.v2x_vehs = []
		self.num_orphan_veh = 0
		

	def setup(self):
		self.background_color = '#d5eeff'
		self.ground = S.Node(parent=self)
		
		# draw roads
		x = 0
		while x <= self.size.w + 64:
			tile = S.SpriteNode('plf:Ground_GrassHalf_mid', position=(x, margin/2))
			self.ground.add_child(tile)
			tile = S.SpriteNode('plf:Ground_GrassHalf_mid', position=(x, margin/2+200))
			self.ground.add_child(tile)
			x += 64

		# draw road markings
		dist_mark_m = 0
		text_font = ('Futura', 10)
		while dist_mark_m < road_length_m:
			dist_marker = S.LabelNode( (str(dist_mark_m)+'m'), text_font, color='black', position=(m2p(-dist_mark_m), 43, 1))
			self.ground.add_child(dist_marker)
			dist_marker = S.LabelNode( (str(dist_mark_m)+'m'), text_font, color='black', position=(m2p(-dist_mark_m), 243, 1))
			self.ground.add_child(dist_marker)
			dist_mark_m += 50

		# draw upper traffic light
		self.t_light_main1 = S.SpriteNode(t_light_body, x_scale=0.65, y_scale=0.75)
		self.t_light_top1 = S.SpriteNode(t_light_end, x_scale=0.65, y_scale=0.8)
		self.t_light_bottom1 = S.SpriteNode(t_light_end, x_scale=0.65, y_scale=0.8)
		self.red_light1 = S.SpriteNode(light, scale=0.6, color='red')
		self.amb_light1 = S.SpriteNode(light, scale=0.6, color='grey')
		self.grn_light1 = S.SpriteNode(light, scale=0.6, color='grey')
		self.add_child(self.t_light_main1)
		self.add_child(self.t_light_top1)
		self.add_child(self.t_light_bottom1)
		self.add_child(self.red_light1)
		self.add_child(self.amb_light1)
		self.add_child(self.grn_light1)
		self.t_light_main1.position = (t_light_x, t_light_y+218)
		self.t_light_top1.position = (t_light_x, t_light_y+262)
		self.t_light_bottom1.position = (t_light_x, t_light_y+181)
		self.t_light_bottom1.run_action (S.Action.rotate_by (-np.pi, 0.01))
		self.red_light1.position = (t_light_x, t_light_y+245,1)
		self.amb_light1.position = (t_light_x, t_light_y+223,1)
		self.grn_light1.position = (t_light_x, t_light_y+201,1)
		
		# draw lower traffic light
		self.t_light_main2 = S.SpriteNode(t_light_body, x_scale=0.65, y_scale=0.75)
		self.t_light_top2 = S.SpriteNode(t_light_end, x_scale=0.65, y_scale=0.8)
		self.t_light_bottom2 = S.SpriteNode(t_light_end, x_scale=0.65, y_scale=0.8)
		self.red_light2 = S.SpriteNode(light, scale=0.6, color='red')
		self.amb_light2 = S.SpriteNode(light, scale=0.6, color='grey')
		self.grn_light2 = S.SpriteNode(light, scale=0.6, color='grey')
		self.add_child(self.t_light_main2)
		self.add_child(self.t_light_top2)
		self.add_child(self.t_light_bottom2)
		self.add_child(self.red_light2)
		self.add_child(self.amb_light2)
		self.add_child(self.grn_light2)
		self.t_light_main2.position = (t_light_x, t_light_y+18)
		self.t_light_top2.position = (t_light_x, t_light_y+62)
		self.t_light_bottom2.position = (t_light_x, t_light_y-19)
		self.t_light_bottom2.run_action (S.Action.rotate_by (-np.pi, 0.01))
		self.red_light2.position = (t_light_x, t_light_y+45,1)
		self.amb_light2.position = (t_light_x, t_light_y+23,1)
		self.grn_light2.position = (t_light_x, t_light_y,1)

		# world titles
		text_font = ('Futura', 20)
		self.world_title1 = S.LabelNode('Orphan World', text_font, color='black', parent=self)
		self.world_title2 = S.LabelNode('GLOSA World', text_font, color='black', parent=self)
		self.world_title1.position = (75, 385, 1)
		self.world_title2.position = (75, 180, 1)
		
		#text_font = ('Futura', 20)
		#self.num_orphan_veh_lbl = S.LabelNode('0', text_font, parent=self)
		#self.num_orphan_veh_lbl.position = (self.size.w/2, self.size.h - 70, 1)
		#self.num_orphan_veh_lbl.z_position = 1

		#self.reset()

	def reset(self):
		# Reset everything to its initial state...
		global t_light_state
		for veh in list(self.orphan_vehs):
			veh.remove_from_parent()
		for veh in list(self.v2x_vehs):
			veh.remove_from_parent()
		self.orphan_vehs = []
		self.v2x_vehs = []
		self.num_orphan_veh = 0
		#self.num_orphan_veh_lbl.text = str(self.num_orphan_veh)
		self.red_light1.color='red'
		self.amb_light1.color='grey'
		self.grn_light1.color='grey'
		self.red_light2.color='red'
		self.amb_light2.color='grey'
		self.grn_light2.color='grey'
		t_light_state = 'red'
		

	def update(self):
		global run_scene
		global start_time
		global run_time
		
		if run_scene == 1:
			if run_time == 0.0:
				
				self.reset()
				self.spawn()
				start_time = self.t - self.dt
				self.scene.speed = 5
			#i = 0
			#while (self.t - start_time) * run_speed < run_time + t_step:
				#i += 1
			run_time = (self.t - start_time) * run_speed
			print 'Running . . . ' + str(int(run_time))+'s'
			#print round(run_time,0)
			if run_time >= sim_time:
				print 'Run Complete'
				run_scene = 0
				run_time = 0.0
			else:
				self.update_lights()
				self.update_vehicles()
			

	def update_lights(self):
		global start_time
		global run_time
		global t_light_state
		#if run_scene == 1 and (self.t - start_time - run_time > t_step) :
		if t_light_state == 'red' and t_light_data[int(run_time/t_step)][3] == 'red_amb':
			t_light_state = 'red_amb'
			self.amb_light1.color='#ffe600'
			self.amb_light2.color='#ffe600'
		if t_light_state == 'red_amb' and t_light_data[int(run_time/t_step)][3] == 'grn':
			t_light_state = 'grn'
			self.red_light1.color='grey'
			self.amb_light1.color='grey'
			self.grn_light1.color='#00ff19'
			self.red_light2.color='grey'
			self.amb_light2.color='grey'
			self.grn_light2.color='#00ff19'
		if t_light_state == 'grn' and t_light_data[int(run_time/t_step)][3] == 'amb':
			t_light_state = 'amb'
			self.amb_light1.color='ffe600'
			self.grn_light1.color='grey'
			self.amb_light2.color='ffe600'
			self.grn_light2.color='grey'
		if t_light_state == 'amb' and t_light_data[int(run_time/t_step)][3] == 'red':
			t_light_state = 'red'
			self.red_light1.color='red'
			self.amb_light1.color='grey'
			self.red_light2.color='red'
			self.amb_light2.color='grey'


	def update_vehicles(self):
		global start_time
		global run_time
		t = int(run_time*10)
		v = 0
		self.num_orphan_veh = 0
		for veh in list (self.orphan_vehs):
			veh.run_action(S.Action.move_to(m2p(orphan_veh_data[v][t][2]), 268))
			
			if orphan_veh_data[v][t][2] >= 0:
				veh.pos_marker.text = ''
				#veh.dist_marker.text = ''
				veh.speed_marker.text = ''
				veh.state_marker.text = ''
			else:
				#veh.dist_marker.text = (str(int(-orphan_veh_data[v][t][2]))+'m')
				veh.speed_marker.text = (str(int(mps2mph(orphan_veh_data[v][t][1])))+'mph')
				veh.state_marker.text = (orphan_veh_data[v][t][3])
		
			if orphan_veh_data[v][t][3] == 'cruise':
				veh.color = '#0016ff'
			elif orphan_veh_data[v][t][3] == 'brake':
				veh.color = '#ff4300'
			elif orphan_veh_data[v][t][3] == 'stop':
				veh.color = '#c100c1'
			elif orphan_veh_data[v][t][3] == 'accel':
				veh.color = '#00c100'
			
			if veh.position.x > t_light_x:
				self.num_orphan_veh += 1
			#self.num_orphan_veh_lbl.text = str(self.num_orphan_veh)
			v += 1
					
		v = 0
		for veh in list(self.v2x_vehs):
			veh.run_action(S.Action.move_to(m2p(v2x_veh_data[v][t][2]), 68))
			#S.TIMING_SINODIAL
			if v2x_veh_data[v][t][2] >= 0:
				veh.pos_marker.text = ''
				#veh.dist_marker.text = ''
				veh.speed_marker.text = ''
				veh.state_marker.text = ''
			else:
				#veh.dist_marker.text = (str(int(-v2x_veh_data[v][t][2]))+'m')
				veh.speed_marker.text = (str(int(mps2mph(v2x_veh_data[v][t][1])))+'mph')
				veh.state_marker.text = (v2x_veh_data[v][t][3])
		
			if v2x_veh_data[v][t][3] == 'cruise':
				veh.color = '#0016ff'
			elif v2x_veh_data[v][t][3] == 'glosa':
				veh.color = '#ff8500'
			elif v2x_veh_data[v][t][3] == 'brake':
				veh.color = '#ff4300'
			elif v2x_veh_data[v][t][3] == 'stop':
				veh.color = '#c100c1'
			elif v2x_veh_data[v][t][3] == 'accel':
				veh.color = '#00c100'
			
			#if veh.position.x > m2p(spat_range):
				#veh.texture = v2x_veh
			v += 1

	def spawn(self):
		text_font = ('Futura', 10)
		for v in range(0,veh_num):
			orphan_veh = Vehicle(parent=self)
			v2x_veh = Vehicle(parent=self)
			orphan_veh.run_action(S.Action.move_to (m2p(approach), 268, 0.01 ))
			v2x_veh.run_action(S.Action.move_to (m2p(approach), 68, 0.01 ))
			orphan_veh.pos_marker.text = (str(v+1))
			v2x_veh.pos_marker.text = (str(v+1))
			self.orphan_vehs.append(orphan_veh)
			self.v2x_vehs.append(v2x_veh)


class PlotView(ui.View):
	def __init__ (self, parent = None):
		self.frame = (10, 20, 1000, 750)
		if parent:
			parent.add_subview(self)
		self.background_color = 'white'
		v= self.superview

	def draw(self):
		self.x_left = 55.0
		self.x_right = 985.0
		self.x_min = x_val_min * x_grid
		self.x_max = x_val_max * x_grid
		self.y_min = y_val_min * y_grid
		self.y_max = y_val_max * y_grid
		
		self.scale_x = (self.x_right - self.x_left) / (self.x_max - self.x_min)
		
		if self.x_max - self.x_min > 1000:
			self.step_x_axis = 100
		elif self.x_max - self.x_min > 400:
			self.step_x_axis = 50
		else:
			self.step_x_axis = x_grid
			
		if self.y_max - self.y_min > 500:
			self.step_y_axis = 100
		else:
			self.step_y_axis = y_grid
		
		if plot_layout == 0:
			self.orphan_y_low = 705.0
			self.orphan_y_high = 65.0
			self.scale_y = (self.orphan_y_high - self.orphan_y_low) / (self.y_max - self.y_min)
			self.plot_v_grid(self.orphan_y_low, self.orphan_y_high)
			self.plot_h_grid(self.orphan_y_low, self.orphan_y_high)
			self.plot_xaxis(self.orphan_y_low, self.orphan_y_high)
			self.plot_orphan(self.orphan_y_low, self.orphan_y_high)
			self.plot_axes(self.orphan_y_low, self.orphan_y_high)
			self.plot_xy_label(self.orphan_y_low, self.orphan_y_high)
			self.plot_title()
		elif plot_layout == 2:
			self.v2x_y_low = 705.0
			self.v2x_y_high = 65.0
			self.scale_y = (self.v2x_y_high - self.v2x_y_low) / (self.y_max - self.y_min)
			self.plot_v_grid(self.v2x_y_low, self.v2x_y_high)
			self.plot_h_grid(self.v2x_y_low, self.v2x_y_high)
			self.plot_xaxis(self.v2x_y_low, self.v2x_y_high)
			self.plot_v2x(self.v2x_y_low, self.v2x_y_high)
			self.plot_axes(self.v2x_y_low, self.v2x_y_high)
			self.plot_xy_label(self.v2x_y_low, self.v2x_y_high)
			self.plot_title()
		elif plot_layout == 1:
			self.orphan_y_low = 365.0
			self.orphan_y_high = 65.0
			self.v2x_y_low = 705.0
			self.v2x_y_high = 405.0
			self.scale_y = (self.orphan_y_high - self.orphan_y_low) / (self.y_max - self.y_min)
			self.plot_v_grid(self.orphan_y_low, self.orphan_y_high)
			self.plot_h_grid(self.orphan_y_low, self.orphan_y_high)
			self.plot_xaxis(self.orphan_y_low, self.orphan_y_high)
			self.plot_orphan(self.orphan_y_low, self.orphan_y_high)
			self.plot_axes(self.orphan_y_low, self.orphan_y_high)
			self.plot_xy_label(self.orphan_y_low, self.orphan_y_high)
			self.plot_v_grid(self.v2x_y_low, self.v2x_y_high)
			self.plot_h_grid(self.v2x_y_low, self.v2x_y_high)
			self.plot_xaxis(self.v2x_y_low, self.v2x_y_high)
			self.plot_v2x(self.v2x_y_low, self.v2x_y_high)
			self.plot_axes(self.v2x_y_low, self.v2x_y_high)
			self.plot_xy_label(self.v2x_y_low, self.v2x_y_high)
			self.plot_title()

	def plot_v_grid(self, g_low, g_high):
		vGridPath = ui.Path()
		ui.set_color('gray')
		for i in range(1,int((self.x_max - self.x_min)/self.step_x_axis)+1):
			vGridPath.move_to(self.x_left + self.step_x_axis * i * self.scale_x, g_low)
			vGridPath.line_to(self.x_left+ self.step_x_axis * i * self.scale_x, g_high)
			xlabel=ui.Label()
			xlabel.font = ('Futura', 10)
			xlabel.text_color = ('black')
			xlabel.alignment = ui.ALIGN_CENTER
			xlabel.text = (str(int(self.x_min + i * self.step_x_axis)))
			xlabel.frame = (self.x_left - 15 + self.step_x_axis * i * self.scale_x, g_low + 5, 30, 10)
			self.add_subview(xlabel)
		vGridPath.line_width = 0.5
		vGridPath.set_line_dash([5])
		vGridPath.stroke()
		xlabel = ui.Label()
		xlabel.font = ('Futura', 10)
		xlabel.text_color = ('black')
		xlabel.alignment = ui.ALIGN_LEFT
		xlabel.text = (str(int(self.x_min)))
		xlabel.frame = (self.x_left, g_low + 5, 30, 10)
		self.add_subview(xlabel)						

	def plot_h_grid(self, g_low, g_high):
		hGridPath = ui.Path()
		ui.set_color('gray')
		for i in range(0,int(self.y_max//self.step_y_axis)):
			print i, self.y_max, int(self.y_max//self.step_y_axis), self.y_max - self.step_y_axis * i
			hGridPath.move_to(self.x_left, g_high + (self.y_max - self.step_y_axis * i) * -self.scale_y)
			hGridPath.line_to(self.x_right, g_high + (self.y_max - self.step_y_axis * i) * -self.scale_y)
			ylabel = ui.Label()
			ylabel.font = ('Futura', 10)
			ylabel.text_color = ('black')
			ylabel.alignment = ui.ALIGN_RIGHT
			ylabel.text = (str(int(self.step_y_axis * i)))
			ylabel.frame = (self.x_left-35, g_low - 5 + (-self.y_min + self.step_y_axis * i) * self.scale_y, 30, 10)
			self.add_subview(ylabel)
		hGridPath.line_width = 0.5
		hGridPath.set_line_dash([5])
		hGridPath.stroke()
		hGridPath = ui.Path()
		ui.set_color('gray')
		for i in range(1,int(abs(self.y_min//self.step_y_axis))):
			hGridPath.move_to(self.x_left, g_low + (-self.y_min + self.step_y_axis * -i) * self.scale_y)
			hGridPath.line_to(self.x_right, g_low + (-self.y_min + self.step_y_axis * -i) * self.scale_y)
			ylabel = ui.Label()
			ylabel.font = ('Futura', 10)
			ylabel.text_color = ('black')
			ylabel.alignment = ui.ALIGN_RIGHT
			ylabel.text = (str(int(self.step_y_axis * -i)))
			ylabel.frame = (self.x_left - 35, g_low - 5 + (-self.y_min + self.step_y_axis * -i) * self.scale_y, 30, 10)
			self.add_subview(ylabel)
		hGridPath.line_width = 0.5
		hGridPath.set_line_dash([5])
		hGridPath.stroke()
			
	def plot_xaxis(self, g_low, g_high):	
		t = self.x_min
		while t < self.x_max-0.1:
			xaxis = ui.Path()
			if t_light_data [int(t*10)][3] == 'grn':
				ui.set_color('#00c100')
			elif t_light_data [int(t*10)][3] == 'red':
				ui.set_color('red')
			else:
				ui.set_color('#ffe600')
			xaxis.move_to(self.x_left + (t-self.x_min) * self.scale_x, g_high + self.y_max * -self.scale_y - 5)
			i = 0.1
			while t_light_data [int(t*10)][3] == t_light_data [int((t+i)*10)][3] and t+i < self.x_max:
				i += 0.1
			xaxis.line_to(self.x_left + (t+i-self.x_min) * self.scale_x, g_high + self.y_max * -self.scale_y - 5)
			xaxis.line_width = 8
			xaxis.stroke()
			t += i

	def plot_orphan(self, g_low, g_high):		
		for v in range(0,veh_num):
			t = self.x_min
			while t < self.x_max:
				i = 0.1
				if orphan_veh_data [v][int(t*10)][3] != 'unspawned' and orphan_veh_data [v][int(t*10)][3] != 'despawned':
					vtrace = ui.Path()
					if orphan_veh_data [v][int(t*10)][3] == 'cruise':
						ui.set_color('#404040')
						vtrace.line_width = 0.5
					elif orphan_veh_data [v][int(t*10)][3] == 'glosa':
						ui.set_color('#0016ff')
						vtrace.line_width = 1
					elif orphan_veh_data [v][int(t*10)][3] == 'brake':
						ui.set_color('#ff4300')
						vtrace.line_width = 1
					elif orphan_veh_data [v][int(t*10)][3] == 'stop':
						ui.set_color('#c100c1')
						vtrace.line_width = 1
					elif orphan_veh_data [v][int(t*10)][3] == 'accel':
						ui.set_color('#00c100')
						vtrace.line_width = 1
					vtrace.move_to(self.x_left + (t-self.x_min) * self.scale_x, g_high + (orphan_veh_data [v][int(t*10)][2] - self.y_max) * self.scale_y)
					
					while orphan_veh_data [v][int(t*10)][3] == orphan_veh_data [v][int((t+i)*10)][3] and t+i < self.x_max:
						if orphan_veh_data [v][int((t+i)*10)][2] < self.y_min:
							vtrace.move_to(self.x_left + (t+i-self.x_min) * self.scale_x, g_high + (orphan_veh_data [v][int((t+i)*10)][2] - self.y_max) * self.scale_y)
						elif orphan_veh_data [v][int((t+i)*10)][2] < self.y_max:
							vtrace.line_to(self.x_left + (t+i-self.x_min) * self.scale_x, g_high + (orphan_veh_data [v][int((t+i)*10)][2] - self.y_max) * self.scale_y)
						i += 0.1
					vtrace.stroke()
				t += i

	def plot_v2x(self, g_low, g_high):		
		for v in range(0,veh_num):
			t = self.x_min
			while t < self.x_max:
				i = 0.1
				if v2x_veh_data [v][int(t*10)][3] != 'unspawned' and v2x_veh_data [v][int(t*10)][3] != 'despawned':
					vtrace = ui.Path()
					if v2x_veh_data [v][int(t*10)][3] == 'cruise':
						ui.set_color('#404040')
						vtrace.line_width = 0.5
					elif v2x_veh_data [v][int(t*10)][3] == 'glosa':
						ui.set_color('#0016ff')
						vtrace.line_width = 1
					elif v2x_veh_data [v][int(t*10)][3] == 'brake':
						ui.set_color('#ff4300')
						vtrace.line_width = 1
					elif v2x_veh_data [v][int(t*10)][3] == 'stop':
						ui.set_color('#c100c1')
						vtrace.line_width = 1
					elif v2x_veh_data [v][int(t*10)][3] == 'accel':
						ui.set_color('#00c100')
						vtrace.line_width = 1
					vtrace.move_to(self.x_left + (t - self.x_min) * self.scale_x, g_high + (v2x_veh_data [v][int(t*10)][2] - self.y_max) * self.scale_y)
					
					while v2x_veh_data [v][int(t*10)][3] == v2x_veh_data [v][int((t+i)*10)][3] and t+i < self.x_max:
						if v2x_veh_data [v][int((t+i)*10)][2] < self.y_min:
							vtrace.move_to(self.x_left + (t+i-self.x_min) * self.scale_x, g_high + (v2x_veh_data [v][int((t+i)*10)][2] - self.y_max) * self.scale_y)
						elif v2x_veh_data [v][int((t+i)*10)][2] < self.y_max:
							vtrace.line_to(self.x_left + (t+i-self.x_min) * self.scale_x, g_high + (v2x_veh_data [v][int((t+i)*10)][2] - self.y_max) * self.scale_y)
						i += 0.1
					vtrace.stroke()
				t += i

	def plot_axes(self, g_low, g_high):
		axesPath = ui.Path()
		ui.set_color('black')
		axesPath.move_to(self.x_left, g_low)
		axesPath.line_to(self.x_right, g_low)
		axesPath.line_to(self.x_right, g_high)
		axesPath.line_to(self.x_left, g_high)
		axesPath.line_to(self.x_left, g_low)
		axesPath.line_width = 2
		axesPath.stroke()

	def plot_title(self):
		tlabel = ui.Label()
		tlabel.font = ('Futura', 20)
		tlabel.text_color = 'black'
		tlabel.alignment = ui.ALIGN_CENTER
		tlabel.text = 'The GLOSA Scenarios'
		tlabel.frame = (self.width*0.5 - 200, 10, 400, 20)
		self.add_subview(tlabel)
		stlabel = ui.Label()
		stlabel.font = ('Futura', 12)
		stlabel.text_color = 'grey'
		stlabel.alignment = ui.ALIGN_CENTER
		stlabel.text = 'Speed Limit = ' + str(int(speed_limit_mph)) + 'mph;  Traffic Density = ' + str(int(density)) + 'vpm;  Driver Variability = ' + str(int(driver_var*100)) + '%;  Signal Cycle = ' + str(int(t_light_cycle)) + 's;  Signal Split = ' + str(int(t_light_split*100)) + '%;  SPAT Range = ' + str(int(spat_range)) + 'm;  Connected Vehicles = ' + str(int(v2x_veh_mix*100)) + '%'
		stlabel.frame = (0, 35, 1000, 20)
		self.add_subview(stlabel)

	def plot_xy_label(self, g_low, g_high):
		xlabel = ui.Label()
		xlabel.font = ('Futura', 15)
		xlabel.text_color = 'black'
		xlabel.alignment = ui.ALIGN_CENTER
		xlabel.text = 'Time (s)'
		xlabel.frame = (self.x_left - 75 +(self.x_max - self.x_min) * 0.5 * self.scale_x, g_low + 20, 150, 15)
		self.add_subview(xlabel)
			
		ylabel= ui.Label()
		ylabel.font = ('Futura', 15)
		ylabel.text_color = 'black'
		ylabel.alignment = ui.ALIGN_CENTER
		ylabel.text = 'Distance (m)'
		ylabel.frame = (self.x_left - 90, g_high + (g_low - g_high)/2, 100, 15)
		rot = ui.Transform.rotation(-np.pi/2)
		ylabel.transform = rot
		self.add_subview(ylabel)

class EnergyView(ui.View):
	def __init__ (self, parent = None):
		self.frame = (10, 20, 1000, 750)
		if parent:
			parent.add_subview(self)
		self.background_color = 'white'
		v= self.superview

	def draw(self):
		self.x_left = 55.0
		self.x_right = 985.0
		self.x_min = -600
		self.x_max = departure
		self.v_min = 0.0
		self.v_max = speed_limit_mph + 10.0
		self.e_min = 0.0
		self.e_max = 30.0
		
		self.v_y_low = 365.0
		self.v_y_high = 65.0
		self.e_y_low = 705.0
		self.e_y_high = 405.0
		self.scale_v = (self.v_y_high - self.v_y_low) / (self.v_max - self.v_min)
		self.scale_e = (self.e_y_high - self.e_y_low) / (self.e_max - self.e_min)
		self.scale_x = (self.x_right - self.x_left) / (self.x_max - self.x_min)
		
		self.plot_v_grid(self.v_y_low, self.v_y_high)
		self.plot_v_grid(self.e_y_low, self.e_y_high)
		self.plot_h_grid(self.v_y_low, self.v_y_high, self.v_min, self.v_max, v_grid, self.scale_v)
		self.plot_h_grid(self.e_y_low, self.e_y_high, self.e_min, self.e_max, e_grid, self.scale_e)
		self.plot_yaxis(self.v_y_low, self.v_y_high)
		self.plot_yaxis(self.e_y_low, self.e_y_high)
		self.plot_axes(self.v_y_low, self.v_y_high)
		self.plot_axes(self.e_y_low, self.e_y_high)
		
		self.plot_velocity(self.v_y_low, self.v_y_high, self.scale_v)
		self.plot_energy(self.e_y_low, self.e_y_high, self.scale_e)
		
		self.plot_xy_label(self.v_y_low, self.v_y_high, self.e_y_low, self.e_y_high)
		self.plot_title()

	def plot_v_grid(self, g_low, g_high):
		vGridPath = ui.Path()
		ui.set_color('gray')
		for i in range(0,int((self.x_max - self.x_min)/y_grid)+1):
			vGridPath.move_to(self.x_left + y_grid * i * self.scale_x, g_low)
			vGridPath.line_to(self.x_left+ y_grid * i * self.scale_x, g_high)
			xlabel=ui.Label()
			xlabel.font = ('Futura', 10)
			xlabel.text_color = ('black')
			xlabel.alignment = ui.ALIGN_CENTER
			xlabel.text = (str(int(self.x_min + i * y_grid)))
			xlabel.frame = (self.x_left - 15 + y_grid * i * self.scale_x, g_low + 5, 30, 10)
			self.add_subview(xlabel)
		vGridPath.line_width = 0.5
		vGridPath.set_line_dash([5])
		vGridPath.stroke()

	def plot_h_grid(self, g_low, g_high, g_min, g_max, g_grid, g_scale):
		hGridPath = ui.Path()
		ui.set_color('gray')
		for i in range(0,int(g_max//g_grid)+1):
			hGridPath.move_to(self.x_left, g_high + (g_max - g_grid * i) * -g_scale)
			hGridPath.line_to(self.x_right, g_high + (g_max - g_grid * i) * -g_scale)
			ylabel = ui.Label()
			ylabel.font = ('Futura', 10)
			ylabel.text_color = ('black')
			ylabel.alignment = ui.ALIGN_RIGHT
			ylabel.text = (str(round(g_grid * i, 0)))
			ylabel.frame = (self.x_left-35, g_low - 5 + (-g_min + g_grid * i) * g_scale, 30, 10)
			self.add_subview(ylabel)
		hGridPath.line_width = 0.5
		hGridPath.set_line_dash([5])
		hGridPath.stroke()
			
	def plot_yaxis(self, g_low, g_high):
		yaxis = ui.Path()
		ui.set_color('black')
		yaxis.move_to(self.x_left - self.x_min * self.scale_x, g_low)
		yaxis.line_to(self.x_left - self.x_min * self.scale_x, g_high)
		yaxis.line_width = 2
		yaxis.stroke()

	def plot_velocity(self, g_low, g_high, g_scale):		
		for v in range(0,veh_num):
			t = 0
			vtrace = ui.Path()
			ui.set_color('#6b6b6b')
			vtrace.line_width = 0.5
			while orphan_veh_data [v][int(t*10)][3] == 'unspawned' or orphan_veh_data [v][int(t*10)][2] < -600:
				t += t_step
			vtrace.move_to(self.x_left + (-self.x_min + orphan_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + mps2mph(orphan_veh_data [v][int(t*10)][4]) * g_scale)
			while orphan_veh_data [v][int(t*10)][3] != 'despawned':	
				vtrace.line_to(self.x_left + (-self.x_min + orphan_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + mps2mph(orphan_veh_data [v][int(t*10)][4]) * g_scale)	
				t += t_step
			vtrace.stroke()
			
		for v in range(0,veh_num):
			t = 0
			vtrace = ui.Path()
			ui.set_color('#ff4300')
			vtrace.line_width = 0.5
			while v2x_veh_data [v][int(t*10)][3] == 'unspawned' or v2x_veh_data [v][int(t*10)][2] < -600:
				t += t_step
			vtrace.move_to(self.x_left + (-self.x_min + v2x_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + mps2mph(v2x_veh_data [v][int(t*10)][4]) * g_scale)
			while v2x_veh_data [v][int(t*10)][3] != 'despawned':	
				vtrace.line_to(self.x_left + (-self.x_min + v2x_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + mps2mph(v2x_veh_data [v][int(t*10)][4]) * g_scale)	
				t += t_step
			vtrace.stroke()
			
		atrace = ui.Path()
		ui.set_color('#6b6b6b')
		atrace.line_width = 5
		atrace.move_to(self.x_left + (-self.x_min + orphan_ave_data [approach + self.x_min][0]) * self.scale_x, g_low + mps2mph(orphan_ave_data [0][1]) * g_scale)
		for i in range (self.x_min + 1, departure, 1):
			atrace.line_to(self.x_left + (-self.x_min + orphan_ave_data [approach + i][0]) * self.scale_x, g_low + mps2mph(orphan_ave_data [approach + i][1]) * g_scale)
		atrace.stroke()
		
		atrace = ui.Path()
		ui.set_color('#ff4300')
		atrace.line_width = 5
		atrace.move_to(self.x_left + (-self.x_min + v2x_ave_data [approach + self.x_min][0]) * self.scale_x, g_low + mps2mph(v2x_ave_data [0][1]) * g_scale)
		for i in range (self.x_min + 1, departure, 1):
			atrace.line_to(self.x_left + (-self.x_min + v2x_ave_data [approach + i][0]) * self.scale_x, g_low + mps2mph(v2x_ave_data [approach + i][1]) * g_scale)
		atrace.stroke()
		
	def plot_energy(self, g_low, g_high, g_scale):		
		for v in range(0,veh_num):
			t = 0
			vtrace = ui.Path()
			ui.set_color('#6b6b6b')
			vtrace.line_width = 0.5
			while orphan_veh_data [v][int(t*10)][3] == 'unspawned' or orphan_veh_data [v][int(t*10)][2] < -600:
				t += t_step
			vtrace.move_to(self.x_left  + (-self.x_min + orphan_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + orphan_veh_data [v][int(t*10)][5] * g_scale)
			while orphan_veh_data [v][int(t*10)][3] != 'despawned':	
				vtrace.line_to(self.x_left + (-self.x_min + orphan_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + orphan_veh_data [v][int(t*10)][5] * g_scale)	
				t += t_step
			vtrace.stroke()
		for v in range(0,veh_num):
			t = 0
			vtrace = ui.Path()
			ui.set_color('#0016ff')
			vtrace.line_width = 0.5
			while v2x_veh_data [v][int(t*10)][3] == 'unspawned' or v2x_veh_data [v][int(t*10)][2] < -600:
				t += t_step
			vtrace.move_to(self.x_left  + (-self.x_min + v2x_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + v2x_veh_data [v][int(t*10)][5] * g_scale)
			while v2x_veh_data [v][int(t*10)][3] != 'despawned':	
				vtrace.line_to(self.x_left + (-self.x_min + v2x_veh_data [v][int(t*10)][2]) * self.scale_x, g_low + v2x_veh_data [v][int(t*10)][5] * g_scale)	
				t += t_step
			vtrace.stroke()
			
		atrace = ui.Path()
		ui.set_color('#6b6b6b')
		atrace.line_width = 5
		atrace.move_to(self.x_left + (-self.x_min + orphan_ave_data [approach + self.x_min][0]) * self.scale_x, g_low + (orphan_ave_data [0][2]) * g_scale)
		for i in range (self.x_min + 1, departure, 1):
			atrace.line_to(self.x_left + (-self.x_min + orphan_ave_data [approach + i][0]) * self.scale_x, g_low + orphan_ave_data [approach + i][2] * g_scale)
		atrace.stroke()
		
		atrace = ui.Path()
		ui.set_color('#0016ff')
		atrace.line_width = 5
		atrace.move_to(self.x_left + (-self.x_min + v2x_ave_data [approach + self.x_min][0]) * self.scale_x, g_low + v2x_ave_data [0][2] * g_scale)
		for i in range (self.x_min + 1, departure, 1):
			atrace.line_to(self.x_left + (-self.x_min + v2x_ave_data [approach + i][0]) * self.scale_x, g_low + v2x_ave_data [approach + i][2] * g_scale)
		atrace.stroke()

	def plot_axes(self, g_low, g_high):
		axesPath = ui.Path()
		ui.set_color('black')
		axesPath.move_to(self.x_left, g_low)
		axesPath.line_to(self.x_right, g_low)
		axesPath.line_to(self.x_right, g_high)
		axesPath.line_to(self.x_left, g_high)
		axesPath.line_to(self.x_left, g_low)
		axesPath.line_width = 2
		axesPath.stroke()

	def plot_title(self):
		tlabel = ui.Label()
		tlabel.font = ('Futura', 20)
		tlabel.text_color = 'black'
		tlabel.alignment = ui.ALIGN_CENTER
		tlabel.text = 'The GLOSA Scenarios'
		tlabel.frame = (self.width*0.5 - 200, 10, 400, 20)
		self.add_subview(tlabel)
		stlabel = ui.Label()
		stlabel.font = ('Futura', 12)
		stlabel.text_color = 'grey'
		stlabel.alignment = ui.ALIGN_CENTER
		stlabel.text = 'Speed Limit = ' + str(int(speed_limit_mph)) + 'mph;  Traffic Density = ' + str(int(density)) + 'vpm;  Driver Variability = ' + str(int(driver_var*100)) + '%;  Signal Cycle = ' + str(int(t_light_cycle)) + 's;  Signal Split = ' + str(int(t_light_split*100)) + '%;  SPAT Range = ' + str(int(spat_range)) + 'm;  Connected Vehicles = ' + str(int(v2x_veh_mix*100)) + '%'
		stlabel.frame = (0, 35, 1000, 20)
		self.add_subview(stlabel)

	def plot_xy_label(self, g1_low, g1_high, g2_low, g2_high):
		xlabel = ui.Label()
		xlabel.font = ('Futura', 15)
		xlabel.text_color = 'black'
		xlabel.alignment = ui.ALIGN_CENTER
		xlabel.text = 'Distance (m)'
		xlabel.frame = (self.x_left - 75 +(self.x_max - self.x_min) * 0.5 * self.scale_x, g1_low + 20, 150, 15)
		self.add_subview(xlabel)
		
		xlabel = ui.Label()
		xlabel.font = ('Futura', 15)
		xlabel.text_color = 'black'
		xlabel.alignment = ui.ALIGN_CENTER
		xlabel.text = 'Distance (m)'
		xlabel.frame = (self.x_left - 75 +(self.x_max - self.x_min) * 0.5 * self.scale_x, g2_low + 20, 150, 15)
		self.add_subview(xlabel)
			
		ylabel= ui.Label()
		ylabel.font = ('Futura', 15)
		ylabel.text_color = 'black'
		ylabel.alignment = ui.ALIGN_CENTER
		ylabel.text = 'Velocity (mph)'
		ylabel.frame = (self.x_left - 90, g1_high + (g1_low - g1_high)/2, 100, 15)
		rot = ui.Transform.rotation(-np.pi/2)
		ylabel.transform = rot
		self.add_subview(ylabel)
		
		ylabel= ui.Label()
		ylabel.font = ('Futura', 15)
		ylabel.text_color = 'black'
		ylabel.alignment = ui.ALIGN_CENTER
		ylabel.text = 'Power (kW)'
		ylabel.frame = (self.x_left - 90, g2_high + (g2_low - g2_high)/2, 100, 15)
		rot = ui.Transform.rotation(-np.pi/2)
		ylabel.transform = rot
		self.add_subview(ylabel)

@ui.in_background
def calc(sender):
	global t_light_data
	global orphan_veh_data
	global v2x_veh_data
	global test_dur
	global speed_limit_mph
	global t_light_split
	global spat_range
	t_light_data = []
	orphan_veh_data = []
	v2x_veh_data = []
	v = sender.superview
	if v['sim_t'].selected_index == 0:
		test_dur = 120.0
	elif v['sim_t'].selected_index == 1:
		test_dur = 300.0
	else:
		test_dur = 600.0
	speed_limit_mph = (v['s_limit'].selected_index + 3) * 10
	t_light_split = float(v['t_split'].selected_index + 4) / 10
	spat_range = (v['spat_r'].selected_index + 3) * 100
	v['run_button'].background_color = 'grey'
	v['plot_button'].background_color = 'grey'
	v['energy_button'].background_color = 'grey'
	calculate()
	v['run_button'].background_color = '#fffff6'
	v['plot_button'].background_color = '#fffff6'
	v['energy_button'].background_color = '#fffff6'


def run(sender):
	global start_time
	global run_scene
	global run_time
	global reset
	print data_calc
	if data_calc == 1:
		# Get the root view:
		#v = sender.superview
		run_scene = 1
		run_time = 0.0
		#print 'run'

#@ui.in_background
def plot(sender):
	global plot_layout
	if data_calc == 1:
		# Get the root view:
		v = sender.superview
		# Get :
		plot_layout = v['plot_choice'].selected_index
		plotarea=ui.View()
		plotarea.background_color='black'
		plotview = PlotView(plotarea)
		plotarea.present(hide_title_bar=True, orientations =['Landscape'])

def energy(sender):
	global plot_layout
	if data_calc == 1:
		# Get the root view:
		v = sender.superview
		# Get :
		plot_layout = v['plot_choice'].selected_index
		energyarea=ui.View()
		energyarea.background_color='black'
		energyview = EnergyView(energyarea)
		energyarea.present(hide_title_bar=True, orientations =['Landscape'])

def v2x_mix_select(sender):
	global v2x_veh_mix
	# Get the root view:
	v = sender.superview
	v2x_veh_mix = round(v['v2x_mix_slider'].value, 1)
	v['v2x_mix_slider'].value = v2x_veh_mix
	v['v2x_mix_label'].text = str(int(v2x_veh_mix * 100))+'%'

def driver_var_select(sender):
	global driver_var
	# Get the root view:
	v = sender.superview
	driver_var = round(v['driver_slider'].value * 4.0, 0) * 0.05
	v['driver_slider'].value = driver_var * 5
	v['driver_var_label'].text = str(int(driver_var * 100))+'%'

def t_light_cycle_select(sender):
	global t_light_cycle
	# Get the root view:
	v = sender.superview
	t_light_cycle = round(v['t_light_cycle_slider'].value, 1) * 100.0 + 20.0
	v['t_light_cycle_slider'].value = (t_light_cycle - 20.0) / 100.0
	v['t_light_cycle_label'].text = str(int(t_light_cycle))+'s'

def t_density_select(sender):
	global density
	# Get the root view:
	v = sender.superview
	density = round(v['t_density_slider'].value * 5.0, 0) * 5.0 + 5.0
	v['t_density_slider'].value = (density - 5.0) / 25.0
	v['t_density_label'].text = str(int(density))+'vpm'
	
def run_speed_select(sender):
	global run_speed
	# Get the root view:
	v = sender.superview
	run_speed = round(v['run_speed_slider'].value * 9.0 + 1.0, 0)
	v['run_speed_slider'].value = (run_speed - 1) / 9.0
	v['run_speed_label'].text = 'x '+str(int(run_speed))

def x_min_select(sender):
	global x_val_min
	# Get the root view:
	v = sender.superview
	x_val_min = (v['x_min_slider'].value * sim_time) // x_grid
	if x_val_min >= x_val_max:
		x_val_min = x_val_max - 1
	v['x_min_slider'].value = x_val_min * x_grid / sim_time
	v['x_min_label'].text = str(int(x_val_min * x_grid))+'s'

def x_max_select(sender):
	global x_val_max
	# Get the root view:
	v = sender.superview
	x_val_max = (v['x_max_slider'].value * sim_time) // x_grid
	if x_val_max <= x_val_min:
		x_val_max = x_val_min + 1
	v['x_max_slider'].value = x_val_max * x_grid / sim_time
	v['x_max_label'].text = str(int(x_val_max * x_grid))+'s'

def y_min_select(sender):
	global y_val_min
	# Get the root view:
	v = sender.superview
	y_val_min = (-approach + v['y_min_slider'].value * approach) // y_grid
	if y_val_min > -1:
		y_val_min = -1
	v['y_min_slider'].value = (approach + y_val_min * y_grid) / approach
	v['y_min_label'].text = str(int(y_val_min * y_grid))+'m'
	
def y_max_select(sender):
	global y_val_max
	# Get the root view:
	v = sender.superview
	y_val_max = (v['y_max_slider'].value * departure) // y_grid
	if y_val_max < 1:
		y_val_max = 1
	v['y_max_slider'].value = y_val_max * y_grid / departure
	v['y_max_label'].text = str(int(y_val_max * y_grid))+'m'
	
def exit(sender):
	# Get the root view:
	v = sender.superview
	v.close()

v = ui.load_view()
v.background_color = 'black'
road_scene = RoadScene()
road_view = RoadView(road_scene, v)
if test_dur == 120.0:
	v['sim_t'].selected_index = 0
elif test_dur == 300.0:
	v['sim_t'].selected_index = 1
else:
	v['sim_t'].selected_index = 2
v['s_limit'].selected_index = int((speed_limit_mph / 10) -3)
v['t_split'].selected_index = int((t_light_split * 10) - 4)
v['spat_r'].selected_index = int((spat_range / 100) - 3)
v['plot_choice'].selected_index = plot_layout
v.present(hide_title_bar=True, orientations =['Landscape'])