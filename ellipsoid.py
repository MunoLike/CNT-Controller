import cv2



def update_min(val):
    global thresh_min
    thresh_min = val


def update_max(val):
    global thresh_max
    thresh_max = val

thresh_min = 0
thresh_max = 0
slctpos= (0,0)


cv2.namedWindow("otsu", cv2.WINDOW_NORMAL)

cv2.createTrackbar("thresh_min", "otsu", 0, 255, update_min)
cv2.createTrackbar("thresh_max", "otsu", 0, 255, update_max)

cap = cv2.imread("tekito.png")

cv2.imshow("src", cap)


hsv=cv2.cvtColor(cap, cv2.COLOR_BGR2HSV)
cv2.imshow("hsv", hsv)


while True:
    if cv2.waitKey(1) != -1:
        break


