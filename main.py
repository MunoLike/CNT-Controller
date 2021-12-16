import numpy as np
import cv2
from datetime import datetime

import cvFpsCalc


def update(val):
    pass

w1_name = 'test'
w2_name = 'diff'
registered = False
present_sum = 0
in_progress = False
counter = 0
wait_cnt = 0

cv2.namedWindow(w1_name, cv2.WINDOW_NORMAL)
cv2.namedWindow(w2_name, cv2.WINDOW_NORMAL)
cv2.createTrackbar("thresh", w2_name, 40, 255, update)
cap = cv2.VideoCapture("output.avi")

cvFpsCalc = cvFpsCalc.CvFpsCalc()

result = open('result.csv', 'w', encoding='utf-8', newline='\n')
result.write(f'Executed time, {datetime.now()}\n')
present_time = datetime.now()


while True:
    ret, frame = cap.read()

    if ret:
        fps = cvFpsCalc.get()
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

            cv2.imshow(w2_name, bined)

            if in_progress:
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

                    present_time = datetime.now()
                    

        if wait_cnt >= 500:
            wait_cnt = 0
            print(fps)
        
        wait_cnt += 1

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