from traceback import print_tb
import pyrealsense2 as rs
import numpy as np
import cv2
import mediapipe as mp
import time

def draw_rectangle(mask_color, frame):
    cn = cv2.findContours(mask_color, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    if len(cn)>0:
        roi = max(cn, key=cv2.contourArea)
        xg, yg, wg, hg = cv2.boundingRect(roi)
        cv2.rectangle(frame, (xg, yg), (xg + wg, yg + hg), (0,255,0), 3)
        
    

# red
red_lower_range = np.array([0, 50, 100])
red_upper_range = np.array([30, 255, 255])

#green
green_lower_range = np.array([40, 50, 75])
green_upper_range = np.array([80, 255, 250])

#blue
blue_lower_range = np.array([90, 50, 50])
blue_upper_range = np.array([150, 255, 255])  


# TESTING PHASE
# Don't forget to set the right path 
img = cv2.imread("C:\\University\\Git stuff\\Intent_Prediction_ROB8\\colors.jpg")   
# img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_REPLICATE)
img = cv2.resize(img, [600,400])
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV_FULL)
mask = cv2.inRange(img_hsv, red_lower_range, red_upper_range)
# draw roi
cn, hierarchry = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
center_points = list()
cv2.drawContours(img, cn, -1, (0,255,0), 3)
i = 0
print(len(cn))
while i < len(cn):
    M = cv2.moments(cn[i])
    if (M['m00']!=0):
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        # center_points += [int(xg+np.floor(wg/2)), int(yg+np.floor(hg/2))]
        center_points.append([cx, cy])
    i+=1
print(center_points)
for center in center_points:
    print(center)
    cv2.circle(img, tuple(center), 0, 0, 5)
cv2.imshow("imga", img)
cv2.imshow("img", mask)
cv2.waitKey(0)

# cap = cv2.VideoCapture(0)

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
        frame_hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        mask_blue = cv2.inRange(frame_hsv, blue_lower_range, blue_upper_range)

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha = 0.03), cv2.COLORMAP_JET)
        draw_rectangle(mask_blue, color_image)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))      
        
        # Show images
        cv2.namedWindow('Project', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Project', images)
        cv2.imshow("frames", mask_blue)
        key = cv2.waitKey(30)
        
        # Esc button
        if key == 27:
            break

finally:

    # Stop streaming
    pipeline.stop()