from traceback import print_tb
import pyrealsense2 as rs
import numpy as np
import cv2

# red
red_lower_range = np.array([0, 50, 100])
red_upper_range = np.array([30, 255, 255])

#green
green_lower_range = np.array([40, 50, 75])
green_upper_range = np.array([80, 255, 250])

#blue
blue_lower_range = np.array([100, 50, 50])
blue_upper_range = np.array([140, 255, 255])  

# # TESTING PHASE
# # Don't forget to set the right path 
# img = cv2.imread("C:\\University\\Git stuff\\Intent_Prediction_ROB8\\colors.jpg")   
# # img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_REPLICATE)
# img = cv2.resize(img, [600,400])
# img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV_FULL)
# mask = cv2.inRange(img_hsv, red_lower_range, red_upper_range)
# # draw roi
# cn, hierarchry = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# center_points = list()
# cv2.drawContours(img, cn, -1, (0,255,0), 3)
# i = 0
# # print(len(cn))
# while i < len(cn):
#     M = cv2.moments(cn[i])
#     cx = int(M['m10']/M['m00'])
#     cy = int(M['m01']/M['m00'])
#     # center_points += [int(xg+np.floor(wg/2)), int(yg+np.floor(hg/2))]
#     center_points.append([cx, cy])
#     i+=1
# # print(center_points)
# for center in center_points:
#     # print(center)
#     cv2.circle(img, tuple(center), 0, 0, 5)
# # cv2.imshow("imga", img)
# # cv2.imshow("img", mask)
# cv2.waitKey(0)

vid = cv2.VideoCapture(0)
while(True):
    ret, frame = vid.read()
    # print("hi")
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
    mask = cv2.inRange(img_hsv, blue_lower_range, blue_upper_range)
    cn, hierarchry = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center_points = list()
    cv2.drawContours(frame, cn, -1, (0,255,0), 3)
    i = 0
    # print(len(cn))
    while i < len(cn):
        M = cv2.moments(cn[i])
        if (M['m00']!=0):
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            # center_points += [int(xg+np.floor(wg/2)), int(yg+np.floor(hg/2))]
            center_points.append([cx, cy])
        i+=1
    # print(center_points)
    for center in center_points:
        # print(center)
        cv2.circle(frame, tuple(center), 0, 0, 5)
    
    
    cv2.imshow("video", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows
