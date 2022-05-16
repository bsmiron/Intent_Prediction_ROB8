from traceback import print_tb
import pyrealsense2 as rs
import numpy as np
import cv2

# red
red_lower_range = np.array([0, 50, 50])
red_upper_range = np.array([10, 255, 255])

# orange
orange_lower_range = np.array([10, 50, 50])
orange_upper_range = np.array([20, 255, 255])

# yellow
yellow_lower_range = np.array([30, 50, 50])
yellow_upper_range = np.array([40, 255, 255])

#green
green_lower_range = np.array([50, 100, 100])
green_upper_range = np.array([80, 255, 255])

#blue 140 - 180
blue_lower_range = np.array([140, 50, 50])
blue_upper_range = np.array([180, 255, 255])  


# Create function for color detection
def get_color(img_hsv, lower, upper):
    mask = cv2.inRange(img_hsv, lower, upper)
    cn, hierarchry = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center_points = list()
    cv2.drawContours(img, cn, -1, (0,255,0), 3)
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
        cv2.circle(img, tuple(center), 0, 0, 5)

# TESTING PHASE
# Don't forget to set the right path 
blue = np.uint8([[[254,0,0]]])
hsv_blue = cv2.cvtColor(blue, cv2.COLOR_BGR2HSV)
print(hsv_blue)
img = cv2.imread("image_colors/colors.jpg")   
img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_REPLICATE)
img = cv2.resize(img, [600,400])
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)


# get_color( img_hsv, red_lower_range, red_upper_range)
# get_color( img_hsv, blue_lower_range, blue_upper_range)
# get_color( img_hsv, green_lower_range, green_upper_range)
get_color(img_hsv, yellow_lower_range, yellow_upper_range)
cv2.imshow("imga", img)

cv2.waitKey(0)

'''
vid = cv2.VideoCapture(0)
while(True):
    ret, frame = vid.read()
     # print("hi")
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV_FULL)
     
    get_color(img_hsv, blue_lower_range, blue_upper_range)
    get_color(img_hsv, red_lower_range, red_upper_range)
    get_color(img_hsv, green_lower_range, green_upper_range)
    
    cv2.imshow("video", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
         break

vid.release()
cv2.destroyAllWindows
'''