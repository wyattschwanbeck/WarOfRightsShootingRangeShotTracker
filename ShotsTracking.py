# -*- coding: utf-8 -*-
"""
The goal of this program is to record shots on War of Rights Shooting range to
assist with accuracy and consistancy in shots.
Currently the code is not dynamic and was written to capture footage via
1920X1080 resolution on a second monitor.
Changing values for monitor variable on the functions Capture_Sights and Capture_Results
will allow you to adjust for screen resolution.
Changing the size of the captured images for either of these may require you to adjust
the paste call on RingBuffers method CreateGif. It is set to paste the lower
"""

import mss
import win32api
import time
import datetime
import os

from PIL import Image
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
		# full, pop the oldest item, left most item
		self.popleft()

	def append(self, item):
		deque.append(self, item)
		# max size reached, append becomes full_append
		if len(self) == self.size:
			self.append = self.full_append

	def get(self):
		"""returns a list of size items (newest items)"""
		return list(self)

	def CreateGif(self, current_date, shot_taken, final_result):
		aim_frames = self.get()
		final_result = Image.frombytes("RGB",
								 final_result.size,
								 final_result.bgra, "raw", "BGRX")
		final_frames = []
		print(len(aim_frames))
		for f,frame in enumerate(aim_frames,0):
			frame = Image.frombytes("RGB",
						   frame.size,
						   frame.bgra, "raw", "BGRX")
			final_result_copy = final_result.copy()
			final_result_copy.paste(frame,
						   (final_result_copy.size[0]-frame.size[0],
							  final_result_copy.size[1]-frame.size[1]))
			final_frames.append(final_result_copy)
			final_frames[0].save(
				"{0}/{1}.gif".format(current_date, shot_taken),
				format="GIF", append_images=final_frames[1:],
				save_all=True, loop=0, fps =30, optimize=True)


def Capture_Result(current_date, shot_taken):
	'''Captures the shooting range result'''
	time.sleep(1)
	with mss.mss() as sct:
		monitor = {"top":210, "left":850, "width":475, "height":225,"mon":1}
		sct_img = sct.grab(monitor)
		return sct_img


def Capture_Sights(current_date, shot_taken, ss_num):
	'''Capture a the last 100 frames since shooting'''
	with mss.mss() as sct:
		monitor = {"top":480, "left":920, "width":80, "height":80,"mon":1}
		if os.path.exists(current_date)==False:
			os.mkdir(current_date)
		if os.path.exists("{0}/{1}".format(current_date,shot_taken)) == False:
			os.mkdir("{0}/{1}".format(current_date,shot_taken))

		sct_img = sct.grab(monitor)
		return sct_img

def Start_Count_Down_Then_Capture(current_date, shot_taken):
	ring = RingBuffer(100)

	print("Count Down Initiated")
	start_time = time.time()
	state_left = win32api.GetKeyState(0x01)

	state_left_time = time.time()
	state_right = win32api.GetKeyState(0x02)

	while time.time()-start_time<4:

		if state_right ==0:
			return False
		else:
			state_right = win32api.GetKeyState(0x02)
	capture_count = 0
	while state_right < 0:
		ring.append(Capture_Sights(current_date,shot_taken,capture_count))
		state_right = win32api.GetKeyState(0x02)
		state_left = win32api.GetKeyState(0x01)
		capture_count+=1

		if state_left < 0:
			state_left_time = time.time()
			while time.time() - state_left_time < .25:
				ring.append(Capture_Sights(current_date,shot_taken,capture_count))

			final_result = Capture_Result(current_date,shot_taken)
			ring.CreateGif(current_date, shot_taken, final_result)
			return True
			break

	return False



shot_taken = 0
while True:
	current_date = datetime.date.today().strftime("%d-%m-%Y")
	state_right = win32api.GetKeyState(0x02)

	if state_right < 0:

		if Start_Count_Down_Then_Capture(current_date,shot_taken):
			shot_taken += 1




