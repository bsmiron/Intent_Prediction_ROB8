import cv2 
import numpy as np

def draw_rectangle(mask_color, frame):
    cn = cv2.findContours(mask_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cn)>0:
        roi = max(cn, key=cv2.contourArea)
        xg, yg, wg, hg = cv2.boundingRect(roi)
        cv2.rectangle(frame, (xg, yg), (xg + wg, yg + hg), (0,255,0), 3)
        middle_x = (xg + xg + wg)/2
        middle_y = (yg + yg + hg)/2
        return middle_x, middle_y
    

#blue
blue_lower_range = np.array([110, 50, 50])
blue_upper_range = np.array([130, 255, 255])  

# red
red_lower_range = np.array([169, 100, 100])
red_upper_range = np.array([189, 255, 255])

#green
green_lower_range = np.array([50, 100, 100])
green_upper_range = np.array([70, 255, 255])


# TESTING PHASE
# img = cv2.imread("image colors\colors.jpg")
# img = cv2.resize(img, [600,400])
# img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# mask = cv2.inRange(img_hsv, lower_range, upper_range)
# # draw roi
# cn = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
# if len(cn)>0:
#     roi = max(cn, key=cv2.contourArea)
#     xg, yg, wg, hg = cv2.boundingRect(roi)
#     cv2.rectangle(img, (xg, yg), (xg + wg, yg + hg), (0,255,0), 3)
# cv2.imshow("imga", img)
# cv2.imshow("img", mask)
# cv2.waitKey(0)

cap = cv2.VideoCapture(0)


while(True):

    ret, frame = cap.read()
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow("frame_hsv", frame_hsv)

    mask_blue = cv2.inRange(frame_hsv, blue_lower_range, blue_upper_range)
    mask_red = cv2.inRange(frame_hsv, red_lower_range, red_upper_range)
    mask_green = cv2.inRange(frame_hsv, green_lower_range, green_upper_range)

    blue_x, blue_y = draw_rectangle(mask_blue, frame)
    red_x, red_y = draw_rectangle(mask_red, frame)
    green_x, green_y = draw_rectangle(mask_green, frame)
    cv2.imshow("Video", frame)
    

    key = cv2.waitKey(1)
    if key == 27:
        break 
