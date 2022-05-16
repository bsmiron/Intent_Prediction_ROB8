import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp
import math
import time


# Adding bounds for colors goes from RED ->>> GREEN ->>> BLUE

# red
red_lower_range = np.array([0, 50, 50])
red_upper_range = np.array([10, 255, 255])

#green
green_lower_range = np.array([50, 100, 255])
green_upper_range = np.array([80, 255, 255])

#blue
blue_lower_range = np.array([140, 50, 50])
blue_upper_range = np.array([180, 255, 255])  

FX = 386.953
FY = 386.953
PPX = 319.307
PPY = 241.853

CamMatrix = np.asarray([[FX, 0.0, PPX, 0],
            		    [0.0, FY, PPY, 0],
             		    [0.0, 0.0, 1.0, 0]])


fPixels = CamMatrix[0,0]

MAX_DISTANCE = 200
TRASHOLD = 20

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
        if (M['m00']!=0):
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


##################################  Inserting part of the detect_color and getting 3D coordinates ########################################################
       
        frame_hsv = cv2.cvtColor(color_image, cv2.COLOR_RGB2HSV)

        x_blue, y_blue, z_blue = get_color(frame_hsv, blue_lower_range, blue_upper_range)
        x_red, y_red, z_red = get_color(frame_hsv, red_lower_range, red_upper_range)
        x_green, y_green, z_green = get_color(frame_hsv, green_lower_range, green_upper_range)
      
        
############################################### Get 3D coordinates #####################################################################

        # x_world_blue, y_world_blue, z_world_blue = get_coordinate(y_blue, x_blue)
        # x_world_red, y_world_red, z_world_red = get_coordinate(y_red, x_red)
        # x_world_green, y_world_green, z_world_green = get_coordinate(y_green, x_green)


############################################## Predefined Points #####################################################################

        # # Test zone
        # test_x, test_y, test_z = get_coordinate(420, 350)
        # cv2.circle(color_image, (420, 350), 5, (255,0,.0), 2, cv2.FILLED)
        # cv2.putText(color_image, "zobj2:{}".format(test_z), (420-100, 350-20), 0, 1, (255,182,193), 2)

        # # Print real-world coordinates of a given point/s
        # # distance_roi = distance_depth(309, 408)
        
        
        # # Drawing ROI for cup and find the distance in centimeter
        # rw_x, rw_y, rw_z = get_coordinate(250, 350)
        # # cv2.rectangle(color_image, (170,340), (448,477), (0,0,255), 4) 
        # cv2.circle(color_image, (250, 350), 5, (255,0,.0), 2, cv2.FILLED)
        # cv2.putText(color_image, "zobj1:{}".format(rw_z), (250-100, 350-20), 0, 1, (255,182,193), 2)


############################################# Hand landmarks/Hand detection ################################################################

        # Drawing hand landmarks
        mp_hand = mp.solutions.hands
        hands = mp_hand.Hands(max_num_hands=1)
        mp.draw = mp.solutions.drawing_utils
        results = hands.process(color_image)
    
        # Drawing the landmark and find the distance centimeter
        if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    for id, lm in enumerate(handLms.landmark):
                        #print(id,lm) id = type of landmark; lm coordinates of the landmark
                        h, w, c = color_image.shape
                        cx, cy = int(lm.x *w), int(lm.y*h)
                        
                        if id == 9:
                            cv2.circle(color_image, (cx,cy), 10, (255,0,255), cv2.FILLED)
                            # distance_lm = distance_depth(cx,cy)
                            hand_x, hand_y, hand_z = get_coordinate(cy, cx) #y and x
                            #cv2.putText(color_image, "x:{0} y:{1} z:{2}".format(rww_x, rww_y, rww_z), (cx-100, cy-20), 0, 1, (255,182,193), 2)
                            obj_blue_score = get_score_attention(hand_x,hand_y,hand_z, x_blue, y_blue, z_blue)
                            obj_red_score = get_score_attention(hand_x,hand_y,hand_z, x_red, y_red, z_red)
                            obj_green_score = get_score_attention(hand_x,hand_y,hand_z, x_green, y_green, z_green)

############################################ Intent Prediction and sending UR5 Coordiantes ##########################################       
                            if min(obj_blue_score, obj_green_score, obj_red_score) == TRASHOLD:
                                ok = 1
                                while ok == 1:                 
                                    if (obj_blue_score < obj_red_score) and (obj_blue_score < obj_green_score):
                                        print("Obj blue")
                                        max(obj_green_score, obj_red_score)
                                        if max == obj_green_score:
                                            ur5_coordinates = x_green, y_green, z_green
                                            time.sleep(15) # wait 15 seconds
                                            ok = 0
                                        else:
                                            ur5_coordinates = x_red, y_red, z_red
                                            time.sleep(15)
                                            ok = 0
                                    elif (obj_red_score < obj_blue_score) and (obj_red_score < obj_green_score):
                                        print("obj red")
                                        max(obj_green_score, obj_blue_score)
                                        if max == obj_green_score:
                                            ur5_coordinates = x_green, y_green, z_green
                                            time.sleep(15)
                                            ok = 0
                                        else:
                                            ur5_coordinates = x_blue, y_blue, z_blue
                                            time.sleep(15)
                                            ok = 0
                                    else:
                                        print("obj green")
                                        max(obj_blue_score, obj_red_score)
                                        if max == obj_blue_score:
                                            ur5_coordinates = x_blue, y_blue, z_blue
                                            time.sleep(15)
                                            ok = 0
                                        else:
                                            ur5_coordinates = x_red, y_red, z_red
                                            time.sleep(15)
                                            ok = 0

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))      
        
        # Show images
        cv2.namedWindow('Project', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Project', images)
        key = cv2.waitKey(30)
        
        # Esc button
        if key == 27:
            break
            

finally:

    # Stop streaming
    pipeline.stop()