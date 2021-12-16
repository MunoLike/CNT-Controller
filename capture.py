#! /usr/bin/env python3 

import cv2
import time
from collections import deque

#Consts
target_pos = (210,27,267,100)
is_color=True

def printCoord(e, x, y,flags, param):
	if e == cv2.EVENT_LBUTTONDOWN:
		print(x,y)

#Setup
cv2.namedWindow("frame")
cv2.setMouseCallback("frame", printCoord)
rec = False

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
capture.set(cv2.CAP_PROP_FPS,120)

fourcc=cv2.VideoWriter_fourcc(*'MJPG')
size=(target_pos[2]-target_pos[0],target_pos[3]-target_pos[1])
save = cv2.VideoWriter('/media/pi/DEFAULT/tekito.avi', fourcc, capture.get(cv2.CAP_PROP_FPS), size, is_color)
#target_pos[2]-target_pos[0],target_pos[3]-target_pos[1]

print(capture.get(cv2.CAP_PROP_FPS))

if capture.isOpened() is False:
  raise IOError

while(True):
  try:
    _,frame=capture.read()
    frame=cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
    frame = frame[target_pos[1]:target_pos[3], target_pos[0]:target_pos[2]]
    if not is_color: frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    cv2.imshow('frame',frame)
    save.write(frame)
    if cv2.waitKey(1) == ord('s'):
        print("start rec")
        rec=True

    if rec == True:
        save.write(frame)

  except KeyboardInterrupt:
    # 終わるときは CTRL + C を押す
    break

  
save.release()
capture.release()
cv2.destroyAllWindows()
