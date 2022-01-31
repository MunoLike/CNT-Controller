import numpy as np
import cv2
from datetime import datetime
import os
import math

import cvFpsCalc
import pid

#variables
registered = False
present_sum = 0
white_sum = 0
in_progress = False
counter = 0
wait_cnt = 0
auto_reset = False
target_flowrate = 0



#consts
W1_NAME = 'test'
W2_NAME = 'diff'
TARGET_POS = (187,10,241,80)
IS_SIM = True
INCR_DROP_THRESH = 118
FIRST_FLOWRATE = 0.8459
LAST_FLOWRATE = 3.383

#callbacks
def update(val):
    pass

def printCoord(e, x, y,flags, param):
	if e == cv2.EVENT_LBUTTONDOWN:
		print(x,y)


#window setup
cv2.namedWindow(W1_NAME, cv2.WINDOW_NORMAL)
cv2.namedWindow(W2_NAME, cv2.WINDOW_NORMAL)
cv2.createTrackbar("thresh", W2_NAME, 25, 255, update)
cv2.createTrackbar("x-orig", W2_NAME, TARGET_POS[0], 640, update)
cv2.createTrackbar("y-orig", W2_NAME, TARGET_POS[1], 480, update)
cv2.setMouseCallback(W1_NAME, printCoord)

#setup camera
if not IS_SIM:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    cap.set(cv2.CAP_PROP_FPS,120)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 50)
else:
    cap = cv2.VideoCapture('output.avi')


if cap.isOpened() is False:
  raise IOError

#setup writer
# fourcc=cv2.VideoWriter_fourcc(*'MJPG')
# size=(target_pos[2]-target_pos[0],target_pos[3]-target_pos[1])
# save = cv2.VideoWriter('/media/pi/DEFAULT/tekito.avi', fourcc, cap.get(cv2.CAP_PROP_FPS), size, True)

#setup fps counter
cvFpsCalc = cvFpsCalc.CvFpsCalc()

#setup droptime writer
now = datetime.now()
result = open(f'result/{now.strftime("%Y%m%d-%H%M%S")}-result.csv', 'w', encoding='utf-8', newline='\n')
result.write(f'Executed time, {now}\n')
present_time = datetime.now()


#setup pid controller

#main loop
while True:
    ret, frame = cap.read()

    if ret:
        fps = cvFpsCalc.get()
        
        if not IS_SIM:
            frame=cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
            origx = cv2.getTrackbarPos('x-orig', W2_NAME)
            origy = cv2.getTrackbarPos('y-orig', W2_NAME)
            frame = frame[origy:origy+(TARGET_POS[3]-TARGET_POS[1]), origx:origx+(TARGET_POS[2]-TARGET_POS[0])]
        
        #if bg is registered
        #calculate diff
        if registered:
            #blur = cv2.blur(frame, (2,2))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mask = cv2.absdiff(gray, bg)
            #thresh:40 maybe proper
            _, bined = cv2.threshold(mask, cv2.getTrackbarPos('thresh', W2_NAME), 255, cv2.THRESH_BINARY)

            pix_sum = np.sum(bined)
            white_sum = pix_sum / 255
            if white_sum >= 500:
                present_sum = white_sum
                in_progress = True
        

            #if drop is going down
            if in_progress:
#                 contours, _ = cv2.findContours(bined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#                 contours = filter(lambda cnt: cv2.contourArea(cnt) > 5, contours)
#                 for i, cnt in enumerate(contours):
#                     ellipse = cv2.fitEllipse(cnt)
#                     
#                     x, y = ellipse[0]
#                     if math.isnan(x) or math.isnan(y):
#                         continue
# 
#                     x, y = ellipse[1]
#                     if math.isnan(x) or math.isnan(y):
#                         continue
# 
# 
#                     frame = cv2.ellipse(frame, ellipse, (0,84,211), thickness=1)

                #check whether it dropped
                if white_sum/present_sum <= 0.5:
                    counter += 1
                    in_progress = False
                    if counter == 1:
                        print('count start!')
                        result.write(f'{counter}, 0\n')
                    else:
                        td = (datetime.now() - present_time).total_seconds()
                        print(td,f'count: {counter}')
                        result.write(f'{counter}, {td}\n')

            
                    #reset
                    present_time = datetime.now()

            #show mask
            cv2.imshow(W2_NAME, bined)

                    

        if wait_cnt >= 500:
            wait_cnt = 0
            print(fps, white_sum)
            auto_reset = True
        wait_cnt += 1
        
        if auto_reset and white_sum <= 100:
            bg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            print('auto bg reset')
            auto_reset = False


        #drop control
        if counter < INCR_DROP_THRESH:
            target_flowrate = FIRST_FLOWRATE
        else:
            target_flowrate = LAST_FLOWRATE

        #TODO: measure drop size
        # if IS_SIM:
            #pid.PID()


        #show raw image
        cv2.imshow(W1_NAME, frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            bg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            registered = True
            print('set bg')
        elif key == ord('r'):
            counter = 0
            print('reset counter')

    else:
        break

cv2.destroyWindow(W1_NAME)
cv2.destroyWindow(W2_NAME)
#firmly closing
result.flush()
os.fsync(result.fileno())
result.close()
