"""
The goal of this program is to record shots on War of Rights Shooting range to
assist with accuracy and consistancy in shots.
Currently the code is dynamic and will capture footage from the game with fullscreen+borderless display settings
"""

import mss
import win32api
import time
import datetime
import os

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


from collections import deque

class RingBuffer(deque):
	"""
	inherits deque, pops the oldest data to make room
	for the newest data when size is reached
	"""
	def __init__(self, size):
		deque.__init__(self)
		self.size = size

	def full_append(self, item):
		deque.append(self, item)
		self.popleft()

	def append(self, item):
		deque.append(self, item)
		if len(self) == self.size:
			self.append = self.full_append

	def get(self):
		"""returns a list of size items (newest items)"""
		return list(self)

	def CreateTargetGif(self, fireSeconds, final_result):
		aim_frames = self.get()
		final_result=Image.fromarray(final_result.astype('uint8'), 'RGB')
		final_frames = []

		font = ImageFont.truetype("font/HeadlinerNo45-59y8.ttf", 20)


		for f,frame in enumerate(aim_frames,0):
			frame =Image.fromarray(frame.astype('uint8'), 'RGBA')
			final_result_copy = final_result.copy()
			final_result_copy.paste(frame,
						   (final_result_copy.size[0]-frame.size[0],
							  final_result_copy.size[1]-frame.size[1]))

			draw = ImageDraw.Draw(final_result_copy)
			draw.rectangle(((0, 00), (final_result.size[0],15)), fill="black")
			draw.text((0, 2),"Seconds from aiming to firing:{0}".format(fireSeconds),(255,255,255),font=font)
			final_frames.append(final_result_copy)
		final_frames[0].save(
			"results/{0}.gif".format(datetime.datetime.now().strftime("%d-%m-%Y %H%M-%S")),
			format="GIF", append_images=final_frames[1:],
			save_all=True, loop=0, fps =30)
	def CreateKillCamGif(self, fireSeconds):
		aim_frames = self.get()
		final_frames = []

		font = ImageFont.truetype("font/HeadlinerNo45-59y8.ttf", 12)


		for f,frame in enumerate(aim_frames,0):
            #Convert image from array
			frame =Image.fromarray(frame.astype('uint8'), 'RGBA')
			draw = ImageDraw.Draw(frame)
            #Add in black rectangle to captured shot where text will be added
			draw.rectangle(((0, 00), (frame.size[0],11)), fill="black")
			draw.text((0, 2),"Seconds from aiming to firing:{0}".format(fireSeconds),(255,255,255),font=font)
			final_frames.append(frame)
		final_frames[0].save(
			"results/{0}.gif".format(datetime.datetime.now().strftime("%d-%m-%Y %H%M-%S")),
			format="GIF", append_images=final_frames[1:],
			save_all=True, loop=0, fps =30)

def Capture_Result(monitorNum):
	'''Captures the shooting range result'''
	time.sleep(1)
	with mss.mss() as sct:
		image = np.array(sct.grab(sct.monitors[monitorNum]))
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	return adjusted_capture(image,810,150,350,525)


def Capture_Sights(monitorNum):
	'''Capture a the last 100 frames since shooting'''
	with mss.mss() as sct:
		image = np.array(sct.grab(sct.monitors[monitorNum]))
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
		return adjusted_capture(image,842,382,225,225)



def Start_Count_Down_Then_Capture(monitorNum, killCamOnly=False):
	ring = RingBuffer(100)

	print("User Aiming")
	start_time = time.time()
	state_left = win32api.GetKeyState(0x01)

	state_left_time = time.time()
	state_right = win32api.GetKeyState(0x02)

	while time.time()-start_time<2:

		if state_right ==0:
			return False
		else:
			state_right = win32api.GetKeyState(0x02)

	capture_count = 0
	while state_right < 0:
		ring.append(Capture_Sights(monitorNum))
		state_right = win32api.GetKeyState(0x02)
		state_left = win32api.GetKeyState(0x01)
		capture_count+=1

		if state_left < 0:
			print("Shot taken, rendering gif")
			state_left_time = time.time()
			while time.time() - state_left_time < .25:

				ring.append(Capture_Sights(monitorNum))

			fireSeconds = round(time.time()-start_time,2)
			final_result = Capture_Result(monitorNum)
			if killCamOnly==False:
				ring.CreateTargetGif(fireSeconds, final_result)
			else:
				ring.CreateKillCamGif(fireSeconds)

			print("Gif rendered, ready to capture next shot")
			return True
			break

	return False

import numpy as np

import cv2

def adjusted_capture(screen, base_pixel_x, base_pixel_y, y_size, x_size):
        '''Allows for dynamic shot capture on (almost) any resolution'''
        screen_w_adj = (screen.shape[0]/1080)
        screen_h_adj = (screen.shape[1]/1920)

        aspect_ratio = screen.shape[0]/screen.shape[1]
        aspect_adj = (1080/1920)/aspect_ratio

        screen = np.array(screen[int((base_pixel_y*(1/aspect_adj))*screen_h_adj):\
									 int((y_size*(screen.shape[0]/1080) \
									  +((base_pixel_y*(1/aspect_adj))*screen_h_adj))),
                                int((base_pixel_x*aspect_adj)*screen_w_adj):\
									int((x_size*(screen.shape[1]/1920) \
							     +(base_pixel_x*aspect_adj)*screen_w_adj)), :])

        #screen = cv2.resize(screen,(x_size,y_size))

        return screen
print("Shot Tracker for War of Rights Shooting Range")
print("Source code: https://github.com/wyattschwanbeck/WarOfRightsShootingRangeShotTracker")

if os.path.exists("results")==False:
	print("Creating folder within exe directory for results")
	os.mkdir("results")
#default for fullscreen+borderless
monitorNum = 1


killCamOnly = input("Enter 1 to capture Target shot results, enter anything else to only render aiming frames which is ideal to capture shots during matches:")

if killCamOnly.strip() == "1":
	killCamOnly = False
else:
	killCamOnly = True

monitorNum = int(monitorNum)

shot_taken = 0

print("Monitoring for aim...")
while True:

	current_date = datetime.date.today().strftime("%d-%m-%Y")
	state_right = win32api.GetKeyState(0x02)

	if state_right < 0:

		if Start_Count_Down_Then_Capture(monitorNum, killCamOnly):
			shot_taken += 1
			print("{0} Shot(s) Logged".format(shot_taken))

		else:
			print("Shot Aborted")


