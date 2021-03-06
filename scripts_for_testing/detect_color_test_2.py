from traceback import print_tb
import pyrealsense2 as rs
import numpy as np
import cv2

# red
red_lower_range = np.array([0, 50, 50])
red_upper_range = np.array([3, 255, 255])

# orange
orange_lower_range = np.array([14, 100, 50])
orange_upper_range = np.array([16, 255, 255])

# yellow
yellow_lower_range = np.array([30, 100, 50])
yellow_upper_range = np.array([34, 255, 255])


# green
green_lower_range = np.array([50, 50, 50])
green_upper_range = np.array([120, 255, 255])

# blue 140 - 180
blue_lower_range = np.array([140, 75, 50])
blue_upper_range = np.array([155, 255, 255])  

# purple
purple_lower_range = np.array([180, 50, 50])
purple_upper_range = np.array([240, 255, 255])  


# Create function for color detection
def get_color(img_hsv, lower, upper):
    mask = cv2.inRange(img_hsv, lower, upper)
    cn, hierarchry = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center_points = list()
    cv2.drawContours(img, cn, -1, (0,255,0), 3)
    i = 0
    print_ok = 0

    while i < len(cn):
        # if lower == red_lower_range and upper == red_upper_range print_ok ==0:
        #     print("detected red ")
            #   print_ok = 1
        # elif lower == blue_lower_range and upper == blue_lower_range print_ok ==0: 
        #     print("detect blue ")
            #   print_ok = 1
        # elif lower == green_lower_range and upper == green_upper_range print_ok ==0:
        #     print("detect green ")
            #   print_ok = 1
        # elif lower == purple_lower_range and upper == purple_upper_range print_ok ==0:
        #     print("detect purple ")
            #   print_ok = 1
        # elif lower == orange_lower_range and upper == orange_upper_range print_ok ==0:
        #     print("detected orange ")
            #   print_ok = 1
        # elif lower == yellow_lower_range and upper ==yellow_upper_range and print_ok ==0:
        #     print("detected yellow ")
            #   print_ok = 1
        perimeter = cv2.arcLength(cn[i],True)
        M = cv2.moments(cn[i])
        if (M['m00'] != 0 and perimeter>1000 and perimeter<1100):
            # print(perimeter)
            # if cv2.contourArea(cn[i]> 2000):
            cv2.drawContours(img, cn, -1, (0,255,0), 3)
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
img = cv2.imread("image_colors/test_pictures_2022_05_21/data/data4.jpeg")   
# img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_REPLICATE)

# scale_percent = 50 # percent of original size
# width = int(img.shape[1] * scale_percent / 100)
# height = int(img.shape[0] * scale_percent / 100)
# dim = (width, height)

# img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)


get_color(img_hsv, red_lower_range, red_upper_range)
get_color(img_hsv, purple_lower_range, purple_upper_range)
# get_color(img_hsv, green_lower_range, green_upper_range)
# get_color(img_hsv, yellow_lower_range, yellow_upper_range)
get_color(img_hsv, blue_lower_range,blue_upper_range)
get_color(img_hsv, orange_lower_range, orange_upper_range)
cv2.imshow("imga", img)
# print("detected red detected purple detected green detected yellow detected blue detected orange ")
cv2.imwrite("image_colors/test_pictures_2022_05_23/results/test_bench_sep_7.jpeg", img)
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