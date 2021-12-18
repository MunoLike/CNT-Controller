import numpy as np
import cv2
from datetime import datetime
import os

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

import cvFpsCalc


#variables
w1_name = 'test'
w2_name = 'diff'
registered = False
present_sum = 0
in_progress = False
counter = 0
wait_cnt = 0
target_pos = (210,27,267,100)
resized = None
bg=None
isCamera = False
is_resize = False

#window setup
# cv2.namedWindow(w1_name, cv2.WINDOW_NORMAL)
# cv2.namedWindow(w2_name, cv2.WINDOW_NORMAL)
# cv2.createTrackbar("thresh", w2_name, 40, 255, update)
# cv2.setMouseCallback(w1_name, printCoord)

#setup camera
if isCamera:
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


#callbacks
def update(val):
    pass

def printCoord(e, x, y,flags, param):
	if e == cv2.EVENT_LBUTTONDOWN:
		print(x,y)

def glinit():
    glutInitWindowPosition(0,0)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE)
    glutInitWindowSize(target_pos[2]-target_pos[0],target_pos[3]-target_pos[1])
    glutCreateWindow("Display")
    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutIdleFunc(idle)
    glutMainLoop()


def idle():
    glutPostRedisplay()

def reshape(w,h):
    glViewport(0,0,w,h)
    glLoadIdentity()
    glOrtho(-w/(target_pos[2]-target_pos[0]), w/(target_pos[2]-target_pos[0]), -h/(target_pos[3]-target_pos[1]), h/(target_pos[3]-target_pos[1]),-1.0,1.0)

def keyboard(key, x, y):
    global counter
    global bg
    global registered

    key=ord(key)
    if key == 'q':
        glutLeaveMainLoop()
    elif key == 's':
        bg = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        registered = True
        print('set bg')
    elif key == 'r':
        counter = 0
        print('reset counter')


#main loop
def draw():
    global registered
    global present_sum
    global in_progress
    global counter
    global wait_cnt
    global resized
    global bg

    ret, frame = cap.read()
    
    if ret:
        fps = cvFpsCalc.get()
        frame=cv2.rotate(frame,cv2.ROTATE_90_CLOCKWISE)
        if is_resize:
            resized = frame[target_pos[1]:target_pos[3], target_pos[0]:target_pos[2]]
        else:
            resized=frame

        #gldraw
        img=cv2.cvtColor(resized,cv2.COLOR_BGR2RGB)
        h,w = img.shape[:2]
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, img)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(1.0,1.0,1.0)

        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,GL_LINEAR)

        glBegin(GL_QUADS)
        glTexCoord2d(0.0,1.0)
        glVertex3d(-1.0,-1.0,0.0)
        glTexCoord2d(1.0,1.0)
        glVertex3d(1.0,-1.0,0.0)
        glTexCoord2d(1.0,0.0)
        glVertex3d(1.0,1.0,0.0)
        glTexCoord2d(0.0,0.0)
        glVertex3d(-1.0,1.0,0.0)
        glEnd()

        glFlush()
        glutSwapBuffers()

        #if bg is registered
        #calculate diff
        if registered:
            blur = cv2.blur(resized, (2,2))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            mask = cv2.absdiff(gray, bg)
            #thresh:40 maybe proper
            _, bined = cv2.threshold(mask, 40, 255, cv2.THRESH_BINARY)
            pix_sum = np.sum(bined)
            white_sum = pix_sum / 255
            if white_sum >= 500:
                present_sum = white_sum
                in_progress = True
            #show mask
            #cv2.imshow(w2_name, bined)
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
        # cv2.imshow(w1_name, frame)
        # key = cv2.waitKey(1)
        # if key == ord('q'):
        #     os.exit(0)
        # elif key == ord('s'):
        #     bg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #     registered = True
        #     print('set bg')
        # elif key == ord('r'):
        #     counter = 0
        #     print('reset counter')
    else:
        glutLeaveMainLoop()


#init
glinit()
result.close()