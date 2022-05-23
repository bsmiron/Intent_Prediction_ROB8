# from asyncio.windows_events import NULL
import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp
import math
import time

# Asking on what is the gazed fixed based on attention map
# what_color = input("On what color is the gazed fixed on? Choose between red, orange, yellow, green, blue, purple: ")
print_ok = 0

# Adding bounds for colors goes from RED ->>> GREEN ->>> BLUE

# red
red_lower_range = np.array([0, 50, 50])
red_upper_range = np.array([10, 255, 255])

# orange
orange_lower_range = np.array([10, 50, 50])
orange_upper_range = np.array([20, 255, 255])

# yellow
yellow_lower_range = np.array([30, 50, 50])
yellow_upper_range = np.array([40, 255, 255])

# green
green_lower_range = np.array([50, 100, 100])
green_upper_range = np.array([80, 255, 255])

# blue 140 - 180
blue_lower_range = np.array([140, 50, 50])
blue_upper_range = np.array([180, 255, 255])   

# purple
purple_lower_range = np.array([200, 75, 100])
purple_upper_range = np.array([240, 255, 255]) 

FX = 386.953
FY = 386.953
PPX = 319.307
PPY = 241.853

# test if picked 
# 0 = no
#         0   1       2        3    4     5
#        red,orange, yellow, green, blue ,purple
picked = [0,   0,      0,      0,    0,    0]

CamMatrix = np.asarray([[FX, 0.0, PPX, 0],
            		    [0.0, FY, PPY, 0],
             		    [0.0, 0.0, 1.0, 0]])


fPixels = CamMatrix[0,0]

MAX_DISTANCE = 200
TRASHOLD = 20

#if obj is higher than pixel 

# Detecting objects based on colors
def get_color(img_hsv, lower, upper):
    mask = cv2.inRange(img_hsv, lower, upper)
    cn, hierarchry = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center_points = list()
    cv2.drawContours(color_image, cn, -1, (0,255,0), 3)
    i = 0
    x = 0
    y = 0
    z = 0
     # print(len(cn))
    while i < len(cn):
        M = cv2.moments(cn[i])
        if (M['m00']!=0 and M['m00']>2000 and M['m00']<7000):
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            # center_points += [int(xg+np.floor(wg/2)), int(yg+np.floor(hg/2))]
            center_points.append([cx, cy])
            x, y, z = get_coordinate(cx,cy)
        i+=1
    # print(center_points)
    for center in center_points:
        # print(center)
        cv2.circle(color_image, tuple(center), 0, 0, 5)
        cv2.putText(color_image, "x:{0} y:{1} z:{2}".format(x, y, z), (cx-100, cy-20), 0, 1, (0,0,0), 2)
    return x, y, z

        

# Get an attention score_depth
def get_score_attention(x_hand, y_hand, z_hand, x_obj, y_obj, z_obj):
    score = math.sqrt((x_hand - x_obj)*(x_hand - x_obj) + (y_hand - y_obj)*(y_hand - y_obj)+ (z_hand - z_obj)*(z_hand - z_obj))
    return score


# Get real world coordinates, not sure if in meter since depthmap is given in mm
def get_coordinate(pixel_y, pixel_x):
     
    matrix = CamMatrix
    u = int(pixel_x)
    v = int(pixel_y)
    #depth = depth_map

    # Can substituate depth with depth_f and eliminate function distance_depth
    depth_f = int(depth_image[pixel_x, pixel_y])/10 #this is in cmeters
    

    # X and Y might be in meters
    X = depth_f*(u-matrix[0][2])/(matrix[0][0])
    Y = depth_f*(v-matrix[1][2])/(matrix[1][1])
    Z = depth_f
    return [int(X), int(Y), int(Z)]

# Create function that calculates Depth Distance aka Z from the middle of a ROI
def distance_depth(point_x, point_y):
    return int(depth_image[point_x, point_y])

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)
e1 = cv2.getTickCount()

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape


################################## Inserting part of the detect_color and getting 3D coordinates ########################################################
       
        frame_hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

        x_blue, y_blue, z_blue = get_color(frame_hsv, blue_lower_range, blue_upper_range)
        if x_blue != None and y_blue != None and z_blue != None:
            print(f"Object blue detected and has the coordinates x:{x_blue}, y:{y_blue}, z:{z_blue}")
        x_red, y_red, z_red = get_color(frame_hsv, red_lower_range, red_upper_range)
        if x_red != None and y_red != None and z_red != None:
            print(f"Object red detected and has the coordinates x:{x_red}, y:{y_red}, z:{z_red}")
        # x_green, y_green, z_green = get_color(frame_hsv, green_lower_range, green_upper_range)
        #if x_green != None and y_green != None and z_green != None and print_ok == 0:
           # print(f"Object green detected and has the coordinates x:{x_green}, y:{y_green}, z:{z_green}")
           # print_ok = 1
        # x_orange, y_orange, z_orange = get_color(frame_hsv, orange_lower_range, orange_upper_range)
        # if x_orange != NULL and y_orange != NULL and z_orange != NULL:
        #     print(f"Object orange detected and has the coordinates x:{x_orange}, y:{y_orange}, z:{z_orange}")
        # x_yellow, y_yellow, z_yellow = get_color(frame_hsv, yellow_lower_range, yellow_upper_range)
        # if x_yellow != NULL and y_yellow != NULL and z_blue != NULL:
        #     print(f"Object yellow detected and has the coordinates x:{x_yellow}, y:{y_yellow}, z:{y_yellow}")
        # x_purple , y_purple, z_purple = get_color(frame_hsv, purple_lower_range, purple_upper_range)
        # if x_purple != NULL and y_purple != NULL and z_purple != NULL:
        #     print(f"Object purple detected and has the coordinates x:{x_purple}, y:{y_purple}, z:{z_purple}")

        mp_hand = mp.solutions.hands
        hands = mp_hand.Hands(max_num_hands=1) # number of hands
        mp.draw = mp.solutions.drawing_utils
        results = hands.process(color_image)

       # Drawing the landmark and find the distance centimeter
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    #print(id,lm) id = type of landmark; lm coordinates of the landmark
                        h, w, c = color_image.shape
                        cx, cy = int(lm.x *w), int(lm.y*h) 
                        if cx>0 and cy>0 and cx < 480 and cy<480:
                            hand_x, hand_y, hand_z = get_coordinate(cy, cx)
                        # if (hand_x != 0 or hand_x != None) and (hand_y!=0 and hand_y!=None) and (hand_z !=0 or hand_z != None):
                            # obj_green_score = get_score_attention(hand_x,hand_y,hand_z, x_green, y_green, z_green)
                            # obj_green_score = int(obj_green_score)
                            # print(f"Object green score is {obj_green_score}")
                        # cv2.putText(color_image, f"Object green score is: {obj_green_score}", (15,15), 0, 1, (0,0,0), 2)
                        if id == 9:
                            cv2.circle(color_image, (cx,cy), 10, (255,0,255), cv2.FILLED)
                            # (255,182,193)
                            cv2.putText(color_image, "x:{0} y:{1} z:{2}".format(hand_x, hand_y, hand_z), (cx-100, cy-20), 0, 1, (0, 0, 0), 2)

                    # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))      
        
        # Show images
        cv2.namedWindow('Project', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Project', images)
        e2 = cv2.getTickCount()
        t = (e2 - e1) / cv2.getTickFrequency()
        cv2.imwrite(f"image_colors/test_pictures_2022_05_22/new_simmulation/test3/new_simulation_{t}.png", images)
        # if t>10: # change it to record what length of video you are interested in
        #     print("Done!")
        #     break
        key = cv2.waitKey(30)
        
        # Esc button
        if key == 27:
            break
            

finally:

    # Stop streaming
    pipeline.stop()