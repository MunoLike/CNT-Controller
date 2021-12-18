import numpy as np
import cv2
from datetime import datetime

import cvFpsCalc

#callbacks
def update(val):
    pass

def printCoord(e, x, y,flags, param):
	if e == cv2.EVENT_LBUTTONDOWN:
		print(x,y)

#variables
w1_name = 'test'
w2_name = 'diff'
registered = False
present_sum = 0
in_progress = False
counter = 0
wait_cnt = 0
target_pos = (210,27,267,100)
isCamera = False

#window setup
cv2.namedWindow(w1_name, cv2.WINDOW_NORMAL)
cv2.namedWindow(w2_name, cv2.WINDOW_NORMAL)
cv2.createTrackbar("thresh", w2_name, 40, 255, update)
cv2.setMouseCallback(w1_name, printCoord)

#setup camera
if isCamera:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    cap.set(cv2.CAP_PROP_FPS,120)
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
result = open('result.csv', 'w', encoding='utf-8', newline='\n')
result.write(f'Executed time, {datetime.now()}\n')
present_time = datetime.now()


#main loop
while True:
    ret, frame = cap.read()

    if ret:
        fps = cvFpsCalc.get()
        
        frame=cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
        #frame = frame[target_pos[1]:target_pos[3], target_pos[0]:target_pos[2]]
        
        #if bg is registered
        #calculate diff
        if registered:
            #blur = cv2.blur(frame, (2,2))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mask = cv2.absdiff(gray, bg)
            #thresh:40 maybe proper
            _, bined = cv2.threshold(mask, cv2.getTrackbarPos('thresh', w2_name), 255, cv2.THRESH_BINARY)

            pix_sum = np.sum(bined)
            white_sum = pix_sum / 255
            if white_sum >= 500:
                present_sum = white_sum
                in_progress = True
        
            #show mask
            cv2.imshow(w2_name, bined)

            #if drop is going down
            if in_progress:
                #check whether it dropped
                if white_sum/present_sum <= 0.1:
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
                    

        if wait_cnt >= 500:
            wait_cnt = 0
            print(fps)
        
        wait_cnt += 1

        #show raw image
        cv2.imshow(w1_name, frame)
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

cv2.destroyWindow(w1_name)
cv2.destroyWindow(w2_name)
result.close()